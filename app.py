import streamlit as st
from supabase import create_client, Client
import os
import json
import ast

# Supabase client
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Fonctions avec Supabase
def load_tickets():
    return supabase.table("tickets").select("*").execute().data

def load_events():
    return supabase.table("events").select("*").execute().data

def save_ticket(ticket):
    ticket["dates"] = json.loads(json.dumps(ticket["dates"]))
    supabase.table("tickets").insert(ticket).execute()

def save_event(event):
    supabase.table("events").insert(event).execute()

def delete_ticket(id_):
    supabase.table("tickets").delete().eq("id", id_).execute()

def delete_event(id_):
    supabase.table("events").delete().eq("id", id_).execute()

def add_participant_to_event(event_id, new_participant):
    event = supabase.table("events").select("*").eq("id", event_id).execute().data[0]
    participants = event["participants"]

    # Convertir en liste si c’est une chaîne de caractères
    if isinstance(participants, str):
        participants = ast.literal_eval(participants)

    if new_participant not in participants:
        participants.append(new_participant)
        supabase.table("events").update({"participants": participants}).eq("id", event_id).execute()

def main():
    st.set_page_config(page_title="Game With You")
    st.title("Game With You")

    st.markdown("""
        <style>
        .rainbow-pastel-border {
            border: 4px solid;
            border-image: linear-gradient(45deg,
                #ff9a9e,
                #fad0c4,
                #fbc2eb,
                #a1c4fd,
                #c2e9fb,
                #d4fc79,
                #96e6a1
            ) 1;
            border-radius: 20px;
            padding: 16px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    JOURS = ["25-05", "27-05"]
    HEURES = ["Matin", "Après-midi", "Soir", "18h"]
    DISPOS = [f"{j} - {h}" for j in JOURS for h in HEURES]

    menu = st.radio("Navigation", ["Événements", "Tickets"], horizontal=True)
    events = load_events()
    tickets = load_tickets()

    if menu == "Événements":
        st.subheader("Événements à venir")
        for e in events:
            with st.container():
                participants = e["participants"]
                if isinstance(participants, str):
                    participants = ast.literal_eval(participants)

                st.markdown(f"""
                    <div class="rainbow-pastel-border">
                        <h4>{e['jeu']} - {e['date']} par {e['createur']}</h4>
                        <p><strong>Participants :</strong> {', '.join(participants)}</p>
                """, unsafe_allow_html=True)

                # Formulaire pour rejoindre l'événement
                with st.expander("Rejoindre cet événement"):
                    with st.form(f"join_event_{e['id']}"):
                        new_pseudo = st.text_input("Ton pseudo", key=f"pseudo_event_{e['id']}")
                        submit_join_event = st.form_submit_button("Rejoindre")
                        if submit_join_event:
                            if not new_pseudo:
                                st.warning("Tu dois entrer un pseudo.")
                            else:
                                add_participant_to_event(e['id'], new_pseudo)
                                st.success("Tu as rejoint l'événement !")
                                st.rerun()

                col1, col2 = st.columns(2)
                with col1:
                    with st.expander(f"Supprimer {e['jeu']}"):
                        confirm = st.checkbox(f"Je confirme la suppression de {e['jeu']}", key=f"confirm_event_{e['id']}")
                        if confirm and st.button("Supprimer définitivement", key=f"delete_event_{e['id']}"):
                            delete_event(e['id'])
                            st.success("Événement supprimé.")
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "Tickets":
        st.subheader("Créer un ticket")
        with st.form("create_ticket"):
            pseudo = st.text_input("Ton pseudo")
            jeu = st.text_input("Nom du jeu")
            dates_raw = st.text_area("Dates et horaires (une par ligne, ex: 22-05-Matin ou 22-05-18h)")
            submitted = st.form_submit_button("Créer le ticket")
            if submitted:
                dates = [d.strip() for d in dates_raw.split("\n") if d.strip()]
                if not pseudo or not jeu or not dates:
                    st.warning("Merci de remplir tous les champs.")
                else:
                    new_ticket = {
                        "pseudo": pseudo,
                        "jeu": jeu,
                        "dates": dates
                    }
                    save_ticket(new_ticket)
                    st.success("Ticket créé !")
                    st.rerun()

        st.subheader("Tickets en attente")
        for t in tickets:
            with st.container():
                st.markdown(f"""
                    <div class="rainbow-pastel-border">
                        <h5>{t['jeu']} par {t['pseudo']}</h5>
                        <p><strong>Dispos proposées :</strong> {', '.join(t['dates'])}</p>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(3)
                with col2:
                    with st.expander(f"Supprimer le ticket n°{t['id']}"):
                        confirm = st.checkbox(f"Je confirme la suppression", key=f"confirm_ticket_{t['id']}")
                        if confirm and st.button("Supprimer définitivement", key=f"delete_ticket_btn_{t['id']}"):
                            delete_ticket(t['id'])
                            st.success("Ticket supprimé.")
                            st.rerun()

                with col1:
                    with st.expander("Proposer session"):
                        with st.form(f"propose_session_{t['id']}"):
                            pseudo2 = st.text_input("Ton pseudo", key=f"join_pseudo_{t['id']}")
                            dates2 = st.multiselect("Choisis tes dispos communes", options=t['dates'], key=f"join_dates_{t['id']}")
                            submit_join = st.form_submit_button("Proposer une session")

                            if submit_join:
                                if not pseudo2:
                                    st.warning("Tu dois entrer ton pseudo.")
                                elif not dates2:
                                    st.warning("Tu dois sélectionner au moins une date.")
                                else:
                                    communes = set(t['dates']).intersection(dates2)
                                    if communes:
                                        new_event = {
                                            "jeu": t['jeu'],
                                            "date": list(communes)[0],
                                            "createur": t['pseudo'],
                                            "participants": [t['pseudo'], pseudo2]
                                        }
                                        save_event(new_event)
                                        delete_ticket(t['id'])
                                        st.success(f"Événement créé pour {new_event['date']} !")
                                        st.rerun()
                                    else:
                                        st.warning("Aucune date en commun.")

                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
