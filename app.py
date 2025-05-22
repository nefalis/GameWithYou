import streamlit as st
import json
import os

DATA_DIR = "data"
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.json")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")

def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def main():
    st.set_page_config(page_title="Game With You")
    st.title("Game With You")

    # # Dates prédéfinies pour les tickets
    JOURS = ["2025-05-23", "2025-05-24", "2025-05-25", "2025-05-26", "2025-05-27"]
    HEURES = ["Matin", "Après-midi", "Soir"]
    DISPOS = [f"{j} - {h}" for j in JOURS for h in HEURES]

    menu = st.sidebar.radio("Navigation", ["Événements", "Tickets"])
    events = load_data(EVENTS_FILE)
    tickets = load_data(TICKETS_FILE)

    if menu == "Événements":
        st.subheader("Événements à venir")
        for i, e in enumerate(events):
            st.markdown(f"**{e['jeu']}** - {e['date']} par {e['createur']}")
            st.write("Participants :", ", ".join(e["participants"]))

            # Suppression de l'événement
            if st.button(f"Supprimer {e['jeu']} ({i})"):
                events.pop(i)
                save_data(EVENTS_FILE, events)
                st.rerun()

            # Modification de l'événement
            with st.expander(f"Modifier {e['jeu']}"):
                with st.form(f"edit_event_{i}"):
                    new_jeu = st.text_input("Nom du jeu", value=e["jeu"], key=f"event_jeu_{i}")
                    if e["date"] not in DISPOS:
                        e["date"] = DISPOS[0]
                    new_date = st.selectbox("Date + heure", DISPOS, index=DISPOS.index(e["date"]), key=f"event_date_{i}")
                    new_participants = st.text_input("Participants (séparés par virgule)", value=", ".join(e["participants"]), key=f"event_part_{i}")
                    if st.form_submit_button("Modifier l'événement"):
                        e["jeu"] = new_jeu
                        e["date"] = new_date
                        e["participants"] = [p.strip() for p in new_participants.split(",") if p.strip()]
                        save_data(EVENTS_FILE, events)
                        st.success("Événement modifié.")
                        st.rerun()

    elif menu == "Tickets":
        st.subheader("Créer un ticket")
        with st.form("create_ticket"):
            pseudo = st.text_input("Ton pseudo")
            jeu = st.text_input("Nom du jeu")
            dates_raw = st.text_area("Dates et horaires (une par ligne, ex: 2025-05-24 - Matin)")
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
                    tickets.append(new_ticket)
                    save_data(TICKETS_FILE, tickets)
                    st.success("Ticket créé !")
                    st.rerun()

        st.subheader("Tickets en attente")
        for i, t in enumerate(tickets):
            with st.expander(f"{t['jeu']} par {t['pseudo']}"):
                st.write("Dispos proposées :", ", ".join(t["dates"]))

                # Suppression du ticket
                if st.button(f"🗑 Supprimer le ticket {i}", key=f"delete_{i}"):
                    tickets.pop(i)
                    save_data(TICKETS_FILE, tickets)
                    st.success("Ticket supprimé.")
                    st.rerun()

                # Modification du ticket
                with st.form(f"edit_ticket_{i}"):
                    new_pseudo = st.text_input("Ton pseudo", value=t["pseudo"], key=f"edit_pseudo_{i}")
                    new_jeu = st.text_input("Nom du jeu", value=t["jeu"], key=f"edit_jeu_{i}")
                    
                    # Vérifier que les dates par défaut sont dans DISPOS
                    valid_dates = [date for date in t["dates"] if date in DISPOS]
                    new_dates = st.multiselect("Dates + heures dispo", DISPOS, default=valid_dates, key=f"edit_dates_{i}")

                    if st.form_submit_button("Modifier le ticket"):
                        t["pseudo"] = new_pseudo
                        t["jeu"] = new_jeu
                        t["dates"] = new_dates
                        save_data(TICKETS_FILE, tickets)
                        st.success("Ticket modifié.")
                        st.rerun()

                # Ajouter un joueur à un ticket
                with st.form(f"propose_session_{i}"):
                    pseudo2 = st.text_input("Ton pseudo", key=f"join_pseudo_{i}")
                    join_options = t["dates"]
                    dates2 = st.multiselect("Choisis tes dispos communes", options=join_options, key=f"join_dates_{i}")
                    submit_join = st.form_submit_button("Proposer une session")

                    if submit_join:
                        if not pseudo2:
                            st.warning("Tu dois entrer ton pseudo.")
                        elif not dates2:
                            st.warning("Tu dois sélectionner au moins une date.")
                        else:
                            # Création événement si une date en commun
                            communes = set(t["dates"]).intersection(dates2)
                            if communes:
                                new_event = {
                                    "jeu": t["jeu"],
                                    "date": list(communes)[0],
                                    "createur": t["pseudo"],
                                    "participants": [t["pseudo"], pseudo2]
                                }
                                events.append(new_event)
                                tickets.pop(i)
                                save_data(EVENTS_FILE, events)
                                save_data(TICKETS_FILE, tickets)
                                st.success(f"Événement créé pour {new_event['date']} !")
                                st.rerun()
                            else:
                                st.warning("Aucune date en commun.")

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    main()
