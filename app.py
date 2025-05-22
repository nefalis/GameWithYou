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

    # Inject pastel rainbow CSS
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
    events = load_data(EVENTS_FILE)
    tickets = load_data(TICKETS_FILE)

    if menu == "Événements":
        st.subheader("Événements à venir")
        for i, e in enumerate(events):
            with st.container():
                st.markdown(f"""
                    <div class="rainbow-pastel-border">
                        <h4>{e['jeu']} - {e['date']} par {e['createur']}</h4>
                        <p><strong>Participants :</strong> {', '.join(e['participants'])}</p>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Supprimer {e['jeu']} ({i})"):
                        events.pop(i)
                        save_data(EVENTS_FILE, events)
                        st.rerun()
                with col2:
                    with st.expander(f"Modifier {e['jeu']}"):
                        with st.form(f"edit_event_{i}"):
                            new_jeu = st.text_input("Nom du jeu", value=e["jeu"], key=f"event_jeu_{i}")
                            if e["date"] not in DISPOS:
                                e["date"] = DISPOS[0]
                            new_date = st.selectbox("Date + heure", DISPOS, index=DISPOS.index(e["date"]), key=f"event_date_{i}")
                            new_participants = st.text_input("Participants ", value=", ".join(e["participants"]), key=f"event_part_{i}")
                            if st.form_submit_button("Modifier l'événement"):
                                e["jeu"] = new_jeu
                                e["date"] = new_date
                                e["participants"] = [p.strip() for p in new_participants.split(",") if p.strip()]
                                save_data(EVENTS_FILE, events)
                                st.success("Événement modifié.")
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
                    tickets.append(new_ticket)
                    save_data(TICKETS_FILE, tickets)
                    st.success("Ticket créé !")
                    st.rerun()

        st.subheader("Tickets en attente")
        for i, t in enumerate(tickets):
            with st.container():
                st.markdown(f"""
                    <div class="rainbow-pastel-border">
                        <h5>{t['jeu']} par {t['pseudo']}</h5>
                        <p><strong>Dispos proposées :</strong> {", ".join(t["dates"])}</p>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

                # Supprimer
                with col2:
                    if st.button(f"Supprimer n°{i}", key=f"delete_{i}"):
                        tickets.pop(i)
                        save_data(TICKETS_FILE, tickets)
                        st.success("Ticket supprimé.")
                        st.rerun()

                # Modifier
                # with col3:
                #     with st.expander("Modifier"):
                #         with st.form(f"edit_ticket_{i}"):
                #             new_pseudo = st.text_input("Ton pseudo", value=t["pseudo"], key=f"edit_pseudo_{i}")
                #             new_jeu = st.text_input("Nom du jeu", value=t["jeu"], key=f"edit_jeu_{i}")
                #             all_options = list(set(DISPOS + t["dates"]))
                #             new_dates = st.multiselect("Dates + heures dispo", options=all_options, default=t["dates"], key=f"edit_dates_{i}")
                #             if st.form_submit_button("Modifier le ticket"):
                #                 t["pseudo"] = new_pseudo
                #                 t["jeu"] = new_jeu
                #                 t["dates"] = new_dates
                #                 save_data(TICKETS_FILE, tickets)
                #                 st.success("Ticket modifié.")
                #                 st.rerun()

                # Proposer session
                with col1:
                    with st.expander("Proposer session"):
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

                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    main()
