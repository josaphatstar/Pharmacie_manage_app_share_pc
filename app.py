from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Optional

import streamlit as st
import pandas as pd

import db
from utils import validate_expiry_date, validate_quantity, normalize_date

# Initialize database on app start
_db_initialized = False
if not _db_initialized:
    db.init_db()
    _db_initialized = True

st.set_page_config(page_title="Pharmacie - Gestion de Stock", page_icon="💊", layout="centered")


def refresh():
    st.rerun()
# Si la sélection du produit change via un callback, on pose un flag et on effectue
# un seul rerun au début du script pour appliquer les changements (évite d'appeler
# st.rerun() depuis l'intérieur d'un callback, ce qui est un no-op).
if st.session_state.get("product_selection_changed"):
    st.session_state.pop("product_selection_changed", None)
    st.rerun()
# --------------- Dialogs ---------------
@st.dialog("Modifier le produit")
def edit_product_dialog(prod_id: int, name: str, quantity: int, expiry: str):
    # Parse expiry to date
    try:
        y, m, d = map(int, expiry.split("-"))
        default_d = date(y, m, d)
    except Exception:
        default_d = date.today() + timedelta(days=1)

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        new_name = st.text_input("Nom du produit", value=name, key=f"dlg_name_{prod_id}")
    with c2:
        new_qty = st.text_input("Quantité", value=str(quantity), key=f"dlg_qty_{prod_id}")
    with c3:
        new_exp = st.date_input("Date d'expiration", value=default_d, key=f"dlg_exp_{prod_id}", format="YYYY-MM-DD")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Enregistrer", type="primary", use_container_width=True, key=f"dlg_save_{prod_id}"):
            # Validation des données saisies
            ok_q, qty_norm, err_q = validate_quantity(new_qty)
            ok_d, iso_date, err_d = validate_expiry_date(new_exp)
            
            if not new_name.strip():
                st.error("Le nom du produit est requis.")
                return
            if not ok_q:
                st.error(err_q)
                return
            if not ok_d:
                st.error(err_d)
                return
            
            # Vérification si les données ont réellement changé
            original_name = name.strip()
            original_quantity = quantity
            original_expiry = expiry
            
            new_name_clean = new_name.strip()
            new_quantity_final = qty_norm or 0
            new_expiry_final = iso_date or normalize_date(new_exp)
            
            # Comparaison des valeurs originales avec les nouvelles
            has_changes = (
                original_name != new_name_clean or
                original_quantity != new_quantity_final or
                original_expiry != new_expiry_final
            )
            
            if not has_changes:
                # Aucune modification détectée
                st.info("Aucune modification détectée. Les données sont identiques.")
                return
            
            # Procéder à la mise à jour seulement si des changements sont détectés
            try:
                db.update_product(prod_id, new_name_clean, new_quantity_final, new_expiry_final)
            except sqlite3.IntegrityError as e:
                if "UNIQUE" in str(e).upper():
                    st.error("Un produit avec ce nom existe déjà.")
                else:
                    st.error(f"Erreur lors de la mise à jour: {e}")
            else:
                st.session_state.show_modify_success = "Produit modifié avec succès"
                refresh()
    with b2:
        if st.button("Annuler", use_container_width=True, key=f"dlg_cancel_{prod_id}"):
            refresh()


@st.dialog("Confirmer la suppression")
def delete_product_dialog(prod_id: int, name: str):
    # Récupérer les informations complètes du produit
    product = db.get_product_by_id(prod_id)
    
    if product:
        qty = int(product['quantity'])
        exp = str(product['expiry_date'])
        
        # Message d'avertissement
        st.error("⚠️ Cette action est irréversible !")
        
        # Informations du produit à supprimer
        st.info("Vous êtes sur le point de supprimer le produit suivant :")
        
        st.markdown(f"**Produit :** {name}")
        st.markdown(f"**Quantité en stock :** {qty}")
        st.markdown(f"**Date d'expiration :** {exp}")
        
        st.divider()
        
        # Boutons d'action
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✓ Oui, supprimer", type="primary", use_container_width=True, key=f"dlg_del_yes_{prod_id}"):
                try:
                    db.delete_product(prod_id)
                except Exception as e:
                    st.error(f"Erreur lors de la suppression: {e}")
                else:
                    st.session_state.show_delete_success = f"✅ Produit '{name}' supprimé avec succès"
                    refresh()
        with b2:
            if st.button("✕ Annuler", use_container_width=True, key=f"dlg_del_no_{prod_id}"):
                refresh()
    else:
        st.error("Produit introuvable")
        if st.button("Fermer", use_container_width=True):
            refresh()


@st.dialog("Confirmer la sortie")
def confirm_stockout_dialog(pending: dict):    
    # Message d'information
    st.info("Veuillez vérifier les informations suivantes :")
    
    # Informations en colonnes
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Produit :** {pending['name']}")
    with col2:
        st.markdown(f"**Motif :** {pending['reason']}")
    
    st.markdown(f"**Quantité :** {pending['qty']}")
    
    st.divider()
    
    # Boutons d'action
    b1, b2 = st.columns(2)
    with b1:
        if st.button("✓ Confirmer la sortie", type="primary", use_container_width=True, key="dlg_confirm_stockout"):
            try:
                db.remove_stock(
                    product_id=pending['id'],
                    quantity=pending['qty'],
                    reason=pending['reason']
                )
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement : {e}")
            else:
                # Message personnalisé selon si le stock atteint zéro
                if pending['new_stock'] == 0:
                    st.session_state.show_stockout_success = "🔴 Sortie de stock enregistrée ! Le produit a été supprimé car le stock est épuisé."
                else:
                    st.session_state.show_stockout_success = "✅ Sortie de stock enregistrée avec succès !"
                del st.session_state["stockout_pending"]
                refresh()
    with b2:
        if st.button("✕ Annuler", use_container_width=True, key="dlg_cancel_stockout"):
            del st.session_state["stockout_pending"]
            refresh()


# --------------- Sidebar ---------------
st.sidebar.title("🔎 Recherche")
search = st.sidebar.text_input("Nom du produit")

st.title("💊 Application de gestion de stock de pharmacie")
st.caption("Ajouter, modifier et supprimer des produits avec validations.")

# --------------- Tabs ---------------
tab_add, tab_manage, tab_stock_out, tab_history = st.tabs(["➕ Ajouter un produit", "📋 Gérer les produits", "📤 Sorties de Stock", "📜 Historique"]) 

# --------------- Add Product Tab ---------------
with tab_add:
    st.subheader("Ajouter un produit")
    
    # Afficher la notification de succès si elle existe
    if "show_success" in st.session_state:
        st.toast(st.session_state.show_success, icon="✅")
        del st.session_state.show_success
    
    # Gérer le vidage du formulaire après succès
    clear_form = st.session_state.get("clear_form", False)
    if clear_form:
        del st.session_state.clear_form
    
    with st.form("add_product_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            name = st.text_input("Nom du produit", placeholder="Paracétamol 500mg", value="")
        with col2:
            qty = st.text_input("Quantité", placeholder="Ex: 12", value="")
        with col3:
            expiry_d = st.date_input("Date d'expiration", value=date.today(), format="YYYY-MM-DD", key="expiry_date" if not clear_form else "expiry_date_cleared")

        submitted = st.form_submit_button("Enregistrer", use_container_width=True)

    if submitted:
        ok_q, qty_norm, err_q = validate_quantity(qty)
        ok_d, iso_date, err_d = validate_expiry_date(expiry_d)

        if not name.strip():
            st.error("Le nom du produit est requis.")
        elif not ok_q:
            st.error(err_q)
        elif not ok_d:
            st.error(err_d)
        else:
            try:
                db.add_product(name=name.strip(), quantity=qty_norm or 0, expiry_date=iso_date or normalize_date(expiry_d))
            except sqlite3.IntegrityError as e:
                if "UNIQUE" in str(e).upper():
                    st.error("Un produit avec ce nom existe déjà.")
                else:
                    st.error(f"Erreur lors de l'ajout: {e}")
            else:
                st.session_state.show_success = "Produit ajouté avec succès"
                # Vider les champs seulement en cas de succès
                st.session_state.clear_form = True
                refresh()

# --------------- Manage Products Tab ---------------
with tab_manage:
    st.subheader("Liste des produits")
    
    # Afficher les notifications si elles existent
    if "show_modify_success" in st.session_state:
        st.toast(st.session_state.show_modify_success, icon="✅")
        del st.session_state.show_modify_success
    
    if "show_delete_success" in st.session_state:
        st.toast(st.session_state.show_delete_success, icon="🗑️")
        del st.session_state.show_delete_success

    rows = db.get_products(search=search)

    if not rows:
        st.info("Aucun produit trouvé ... ")
    else:
        # Build DataFrame-like structure
        data = []
        today = date.today()
        for r in rows:
            rid = int(r["id"])  # type: ignore[index]
            nm = str(r["name"])  # type: ignore[index]
            qty = int(r["quantity"])  # type: ignore[index]
            ex = str(r["expiry_date"])  # type: ignore[index]
            try:
                y, m, d = map(int, ex.split("-"))
                ex_d = date(y, m, d)
                days_left = (ex_d - today).days
            except Exception:
                days_left = 0
            data.append({
                "Code": rid,
                "Désignation": nm,
                "Quantité": qty,
                "Date d'Expiration": ex,
                "Jours avant Expiration": days_left,
            })

        import pandas as pd

        df = pd.DataFrame(data)

        # Toggle colors
        if "show_colors" not in st.session_state:
            st.session_state.show_colors = True

        top_controls = st.columns([1, 3])
        with top_controls[0]:
            if st.button("Afficher/Masquer Couleurs", use_container_width=True):
                st.session_state.show_colors = not st.session_state.show_colors
        with top_controls[1]:
            if st.session_state.show_colors:
                # Légende dynamique avec cadre dédié
                st.markdown("""
                <div style="
                    border: 2px solid #ddd; 
                    border-radius: 10px; 
                    padding: 15px; 
                    background-color: #f9f9f9;
                    margin: 10px 0;
                ">
                    <h4 style="margin-top: 0; color: #333; text-align: center;">🎨 Code Couleur - État des Stocks</h4>
                    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                        <div style="text-align: center; margin: 5px;">
                            <div style="
                                background-color: #e8f5e8; 
                                border: 1px solid #4CAF50; 
                                border-radius: 8px; 
                                padding: 8px 12px; 
                                margin-bottom: 5px;
                                font-weight: bold;
                            ">🟢 EXCELLENT</div>
                            <small style="color: #666;">Plus de 90 jours</small>
                        </div>
                        <div style="text-align: center; margin: 5px;">
                            <div style="
                                background-color: #fff8dc; 
                                border: 1px solid #FFC107; 
                                border-radius: 8px; 
                                padding: 8px 12px; 
                                margin-bottom: 5px;
                                font-weight: bold;
                            ">🟡 À SURVEILLER</div>
                            <small style="color: #666;">30 à 90 jours</small>
                        </div>
                        <div style="text-align: center; margin: 5px;">
                            <div style="
                                background-color: #ffe4e1; 
                                border: 1px solid #f44336; 
                                border-radius: 8px; 
                                padding: 8px 12px; 
                                margin-bottom: 5px;
                                font-weight: bold;
                            ">🔴 URGENT</div>
                            <small style="color: #666;">Moins de 30 jours</small>
                        </div>
                    </div>
                    <p style="text-align: center; margin-bottom: 0; font-size: 12px; color: #888;">
                        💡 Basé sur le nombre de jours avant expiration
                    </p>
                </div>
                """, unsafe_allow_html=True)

        if st.session_state.show_colors:
            def color_rows(row):
                days_left = row["Jours avant Expiration"]
                if days_left > 90:
                    color = "background-color: #e8f5e8"  # Vert très clair
                elif days_left >= 30:  # Entre 30 et 90 jours (inclus)
                    color = "background-color: #fff8dc"  # Jaune très clair (cornsilk)
                else:  # < 30 jours
                    color = "background-color: #ffe4e1"  # Rouge très clair (mistyrose)
                return [color] * len(row)

            styler = df.style.apply(color_rows, axis=1)
            st.dataframe(styler, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Selection + action buttons
        # Créer des options avec nom + date d'expiration pour différencier les produits
        options = []
        product_map = {}
        
        # Compter les occurrences de chaque nom de produit
        name_counts = {}
        for _, row in df.iterrows():
            name = row['Désignation']
            name_counts[name] = name_counts.get(name, 0) + 1
        
        # Créer les options d'affichage
        for _, row in df.iterrows():
            product_id = int(row['Code'])
            name = row['Désignation']
            qty = int(row['Quantité'])
            exp = str(row["Date d'Expiration"])
            days_left = row["Jours avant Expiration"]
            
            # Si le nom est unique, afficher seulement le nom
            # Sinon, afficher nom + date d'expiration pour différencier
            if name_counts[name] == 1:
                display_label = name
            else:
                # Format avec espaces non-sécables pour les produits en doublon
                display_label = f"{name}\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0→\u00A0\u00A0Exp: {exp}"
            
            options.append(display_label)
            
            # Stocker toutes les infos du produit
            product_map[display_label] = {
                'id': product_id,
                'name': name,
                'quantity': qty,
                'expiry': exp,
                'days_left': days_left
            }

        selected_label = st.selectbox("Sélectionner un produit :", options, index=0 if options else None)
        selected_product = product_map.get(selected_label)
        selected_id = selected_product['id'] if selected_product else None

        btn_cols = st.columns([1, 1, 2])
        with btn_cols[0]:
            if st.button("Modifier", use_container_width=True, disabled=selected_id is None):
                if selected_product is not None:
                    edit_product_dialog(
                        selected_product['id'], 
                        selected_product['name'], 
                        selected_product['quantity'], 
                        selected_product['expiry']
                    )
        with btn_cols[1]:
            if st.button("Supprimer", use_container_width=True, disabled=selected_id is None):
                if selected_product is not None:
                    delete_product_dialog(selected_product['id'], selected_product['name'])
        with btn_cols[2]:
            st.empty()

# --------------- Stock Out Tab ---------------
with tab_stock_out:
    st.subheader("📤 Enregistrer une sortie de stock")
    st.caption("Sélectionnez un produit et indiquez la quantité à retirer du stock.")
    
    # Afficher la notification de succès si elle existe
    if "show_stockout_success" in st.session_state:
        st.toast(st.session_state.show_stockout_success, icon="✅")
        del st.session_state.show_stockout_success

    # Récupérer la liste des produits
    all_products = db.get_products()
    if not all_products:
        st.info("Aucun produit disponible en stock.")
    else:
        # Préparer les données pour le selectbox
        product_options = []
        product_info = {}
        for p in all_products:
            pid = int(p["id"])
            name = str(p["name"])
            qty = int(p["quantity"])
            exp = str(p["expiry_date"])
            display_text = f"{name} (Stock: {qty}) - Exp: {exp}"
            product_options.append(display_text)
            product_info[display_text] = {"id": pid, "name": name, "qty": qty, "exp": exp}

        # Sélection du produit (en dehors du formulaire pour rendre le changement réactif)
        selected_product = st.selectbox(
            "Sélectionner le produit :",
            options=product_options,
            index=0 if product_options else None,
            key="stockout_selected",
            on_change=lambda: st.session_state.__setitem__("product_selection_changed", True),
        )

        # If a stockout is pending confirmation, show confirmation modal
        if "stockout_pending" in st.session_state:
            pending = st.session_state["stockout_pending"]
            confirm_stockout_dialog(pending)

        with st.form("stock_out_form"):

            if selected_product:
                current_stock = product_info[selected_product]["qty"]
                
                # Vérifier si le stock est disponible
                if current_stock == 0:
                    st.warning("⚠️ Ce produit n'a plus de stock disponible.")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Quantité à retirer
                    qty_to_remove = st.number_input(
                        "Quantité à retirer",
                        min_value=1,
                        max_value=max(1, current_stock),
                        value=1 if current_stock > 0 else 1,
                        step=1,
                        disabled=current_stock == 0
                    )
                with col2:
                    # Raison de la sortie
                    reason = st.selectbox(
                        "Motif de la sortie",
                        options=["💰 Vente", "⚠️ Périmé", "🎁 Donné", "📝 Autre"],
                        index=0
                    )

                # Commentaire additionnel
                details = st.text_area(
                    "Commentaire (optionnel)",
                    placeholder="Ajoutez des détails supplémentaires ici...",
                    max_chars=200
                )

                # État du stock après la sortie
                new_stock = current_stock - qty_to_remove

                submitted = st.form_submit_button(
                    "Enregistrer la sortie",
                    type="primary",
                    use_container_width=True,
                    disabled=current_stock == 0
                )

                if submitted:
                    # Store pending confirmation in session_state and rerun to show confirmation panel
                    detail_msg = reason
                    if details:
                        detail_msg += f" - {details}"
                    st.session_state["stockout_pending"] = {
                        "id": product_info[selected_product]["id"],
                        "name": product_info[selected_product]["name"],
                        "qty": int(qty_to_remove),
                        "reason": detail_msg,
                        "details": details,
                        "current_stock": current_stock,
                        "new_stock": new_stock,
                    }
                    st.rerun()

# --------------- History Tab ---------------
with tab_history:
    st.subheader("📜 Historique des opérations")
    st.caption("Toutes les opérations effectuées sur les produits sont enregistrées automatiquement.")
    
    # Filtres pour l'historique
    filter_cols = st.columns([2, 1, 1])
    with filter_cols[0]:
        operation_filters = st.multiselect(
            "Filtrer par opération(s) :",
            ["AJOUT", "MODIFICATION", "SUPPRESSION"],
            placeholder="Choisir une option",
            help="Sélectionnez une ou plusieurs opérations à afficher. Laissez vide pour tout afficher."
        )
    with filter_cols[1]:
        limit_records = st.number_input("Nombre d'enregistrements", min_value=10, max_value=500, value=50, step=10)
    with filter_cols[2]:
        st.empty()
    
    # Récupérer l'historique selon les filtres
    if not operation_filters:  # Si aucun filtre sélectionné, afficher tout
        history_rows = db.get_history(limit=limit_records)
    else:
        # Récupérer les enregistrements pour chaque opération sélectionnée
        all_history = []
        for operation in operation_filters:
            rows = db.get_history_by_operation(operation, limit=limit_records)
            all_history.extend(rows)
        
        # Trier par timestamp décroissant et limiter
        all_history.sort(key=lambda x: x["timestamp"], reverse=True)  # type: ignore[index]
        history_rows = all_history[:limit_records]
    
    if not history_rows:
        st.info("Aucune opération enregistrée pour le moment.")
    else:
        # Construire le DataFrame pour l'historique
        history_data = []
        for h in history_rows:
            # Formater la date/heure
            timestamp = str(h["timestamp"])  # type: ignore[index]
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%d/%m/%Y %H:%M:%S")
            except:
                formatted_time = timestamp
            
            # Définir l'icône selon l'opération
            operation = str(h["operation"])  # type: ignore[index]
            if operation == "AJOUT":
                icon = "➕"
            elif operation == "MODIFICATION":
                icon = "✏️"
            elif operation == "SUPPRESSION":
                icon = "🗑️"
            else:
                icon = "📤"
            
            history_data.append({
                "Date/Heure": formatted_time,
                "Opération": f"{icon} {operation}",
                "Produit": str(h["product_name"] or ""),  # type: ignore[index]
                "Détails": str(h["details"] or ""),  # type: ignore[index]
            })
        
        # Afficher le tableau d'historique
        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        # Statistiques rapides
        st.subheader("📊 Statistiques")
        stats_cols = st.columns(4)
        
        total_operations = len(history_rows)
        ajouts = len([h for h in history_rows if h["operation"] == "AJOUT"])  # type: ignore[index]
        modifications = len([h for h in history_rows if h["operation"] == "MODIFICATION"])  # type: ignore[index]
        suppressions = len([h for h in history_rows if h["operation"] == "SUPPRESSION"])  # type: ignore[index]
        
        with stats_cols[0]:
            st.metric("Total opérations", total_operations)
        with stats_cols[1]:
            st.metric("➕ Ajouts", ajouts)
        with stats_cols[2]:
            st.metric("✏️ Modifications", modifications)
        with stats_cols[3]:
            st.metric("🗑️ Suppressions", suppressions)

# --------------- Backup automatique en arrière-plan ---------------
# Le système de backup fonctionne automatiquement sans interface utilisateur
