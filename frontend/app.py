import requests
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


# The Username & Password of the currently logged-in User, this is used as a pseudo-cookie, as such this is not session-specific.
username = None
password = None

session_data = dict()


def save_to_session(key, value):
    session_data[key] = value


def load_from_session(key):
    return (
        session_data.pop(key) if key in session_data else None
    )  # Pop to ensure that it is only used once


def succesful_request(r):
    return r.status_code in [200, 201]


def convert_status(status):
    # Mapping
    if status == "Don't Participate":
        return "NO"
    if status == "Participate":
        return "YES"
    if status == "Maybe Participate":
        return "MAYBE"
    # Reverse mapping
    if status == "NO":
        return "Don't Participate"
    if status == "YES":
        return "Participate"
    if status == "MAYBE":
        return "Maybe Participate"
    # Default
    return "PENDING"


@app.route("/")
def home():
    global username

    if username is None:
        return render_template("login.html", username=username, password=password)
    else:
        # ================================
        # FEATURE (list of public events)
        #
        # Retrieve the list of all public events. The webpage expects a list of (title, date, organizer) tuples.
        # Try to keep in mind failure of the underlying microservice
        # =================================
        public_events = []
        try:
            response = requests.get("http://backend:8000/api/events/public")
        except requests.exceptions.ConnectionError:
            return render_template(
                "home.html", username=username, password=password, events=public_events
            )

        if succesful_request(response):
            public_events = [
                (event["id"], event["title"], event["date"], event["organizer"])
                for event in response.json()["events"]
            ]

        return render_template(
            "home.html", username=username, password=password, events=public_events
        )


@app.route("/event", methods=["POST"])
def create_event():
    title, description, date, publicprivate, invites = (
        request.form["title"],
        request.form["description"],
        request.form["date"],
        request.form["publicprivate"],
        request.form["invites"],
    )
    # ==========================
    # FEATURE (create an event)
    #
    # Given some data, create an event and send out the invites.
    # ==========================

    global username

    # Create the event
    try:
        response = requests.post(
            "http://backend:8000/api/events",
            json={
                "title": title,
                "description": description,
                "date": date,
                "organizer": username,
                "isPublic": publicprivate == "public",
            },
        )
    except requests.exceptions.ConnectionError:
        return redirect("/")

    if succesful_request(response):
        # Send out the invites
        event_id = response.json()["event"]["id"]
        for invitee in invites.split(";"):
            if not invitee:
                continue
            try:
                requests.post(
                    "http://backend:8000/api/invites",
                    json={
                        "eventId": event_id,
                        "username": invitee,
                        "status": "PENDING",
                    },
                )
            except requests.exceptions.ConnectionError:
                break  # If server is down, don't continue sending invites
        try:
            # Add yourself as participating (you are the organizer)
            requests.post(
                "http://backend:8000/api/invites",
                json={
                    "eventId": event_id,
                    "username": username,
                    "status": "YES",
                },
            )
        except requests.exceptions.ConnectionError:
            pass

    return redirect("/")


@app.route("/calendar", methods=["GET", "POST"])
def calendar():
    calendar_user = (
        request.form["calendar_user"] if "calendar_user" in request.form else username
    )

    # ================================
    # FEATURE (calendar based on username)
    #
    # Retrieve the calendar of a certain user. The webpage expects a list of (id, title, date, organizer, status, Public/Private) tuples.
    # Try to keep in mind failure of the underlying microservice
    # =================================

    if calendar_user != username:
        try:
            response = requests.get(
                f"http://backend:8000/api/shares/by/{calendar_user}/with/{username}"
            )
            success = succesful_request(response)
        except requests.exceptions.ConnectionError:
            success = False
    else:
        success = True

    if success:
        calendar = []
        try:
            # Get the private events that the user is participating in
            response = requests.get(
                f"http://backend:8000/api/invites?username={calendar_user}"
            )
        except requests.exceptions.ConnectionError:
            response = None

        if response is not None and succesful_request(response):
            events = [
                invite["eventId"]
                for invite in response.json()["invites"]
                if invite["status"] in ["YES", "MAYBE"]
            ]
            for event in events:
                try:
                    response = requests.get(f"http://backend:8000/api/events/{event}")
                except requests.exceptions.ConnectionError:
                    break  # If server is down, don't continue fetching events

                if succesful_request(response):
                    event = response.json()["event"]
                    calendar.append(
                        (
                            event["id"],
                            event["title"],
                            event["date"],
                            event["organizer"],
                            "Going",
                            "Public" if event["isPublic"] else "Private",
                        )
                    )

        try:
            response = requests.get(
                f"http://backend:8000/api/rsvp?username={calendar_user}"
            )
        except requests.exceptions.ConnectionError:
            response = None

        if response is not None and succesful_request(response):
            events = [
                (rsvp["eventId"], rsvp["status"])
                for rsvp in response.json()["responses"]
                if rsvp["status"] in ["YES", "MAYBE"]
            ]
            for event, status in events:
                try:
                    response = requests.get(f"http://backend:8000/api/events/{event}")
                except requests.exceptions.ConnectionError:
                    break  # If server is down, don't continue fetching events
                if succesful_request(response):
                    event = response.json()["event"]
                    calendar.append(
                        (
                            event["id"],
                            event["title"],
                            event["date"],
                            event["organizer"],
                            "Going" if status == "YES" else "Maybe going",
                            "Public" if event["isPublic"] else "Private",
                        )
                    )
    else:
        calendar = None

    save_to_session("success", success)

    return render_template(
        "calendar.html",
        username=username,
        password=password,
        calendar_user=calendar_user,
        calendar=calendar,
        success=success,
    )


@app.route("/share", methods=["GET"])
def share_page():
    return render_template(
        "share.html", username=username, password=password, success=None
    )


@app.route("/share", methods=["POST"])
def share():
    share_user = request.form["username"]

    # ========================================
    # FEATURE (share a calendar with a user)
    #
    # Share your calendar with a certain user. Return success = true / false depending on whether the sharing is succesful.
    # ========================================
    global username

    try:
        response = requests.post(
            "http://backend:8000/api/shares",
            json={"sharingUser": username, "receivingUser": share_user},
        )

        success = succesful_request(response)
        save_to_session("success", success)
    except requests.exceptions.ConnectionError:
        success = False

    return render_template(
        "share.html", username=username, password=password, success=success
    )


@app.route("/event/<eventid>")
def view_event(eventid):

    # ================================
    # FEATURE (event details)
    #
    # Retrieve additional information for a certain event parameterized by an id. The webpage expects a (title, date, organizer, status, (invitee, participating)) tuples.
    # Try to keep in mind failure of the underlying microservice
    # =================================
    global username

    try:
        response = requests.get(f"http://backend:8000/api/events/{eventid}")
        if not succesful_request(response):
            return "Event not found", 404
    except requests.exceptions.ConnectionError:
        return "Event not found", 404

    event = response.json()["event"]

    if event["isPublic"] or event["organizer"] == username:
        success = True
    else:
        try:
            # Check if the user is invited
            response = requests.get(
                f"http://backend:8000/api/invites?eventId={eventid}&username={username}"
            )
            success = succesful_request(response)
        except requests.exceptions.ConnectionError:
            success = False
        if not success:
            try:
                # Check if the user shares their calendar with the organizer
                response = requests.get(
                    f"http://backend:8000/api/shares/by/{event['organizer']}/with/{username}"
                )
                success = succesful_request(response)
            except requests.exceptions.ConnectionError:
                success = False

    if success:
        try:
            # Get the participants
            response = requests.get(
                f"http://backend:8000/api/invites?eventId={eventid}"
            )

            if not succesful_request(response):
                return "Event not found", 404
        except requests.exceptions.ConnectionError:
            return "Event not found", 404

        participants = [
            [invite["username"], convert_status(invite["status"])]
            for invite in response.json()["invites"]
            if invite["status"] in ["YES", "MAYBE"]
        ]

        # If the event is public, get the RSVPs
        if event["isPublic"]:
            try:
                response = requests.get(
                    f"http://backend:8000/api/rsvp?eventId={eventid}"
                )
                if succesful_request(response):
                    participants += [
                        [rsvp["username"], convert_status(rsvp["status"])]
                        for rsvp in response.json()["responses"]
                        if rsvp["status"] in ["YES", "MAYBE"]
                    ]
            except requests.exceptions.ConnectionError:
                pass

        event = [
            event["title"],
            event["date"],
            event["organizer"],
            "Public" if event["isPublic"] else "Private",
            participants,
            event["id"],
        ]
    else:
        event = None  # No success, so don't fetch the data

    save_to_session("success", success)

    return render_template(
        "event.html", username=username, password=password, event=event, success=success
    )


@app.route("/login", methods=["POST"])
def login():
    req_username, req_password = request.form["username"], request.form["password"]

    # ================================
    # FEATURE (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    try:
        response = requests.post(
            "http://backend:8000/api/auth/login",
            json={"username": req_username, "password": req_password},
        )

        success = succesful_request(response)
    except requests.exceptions.ConnectionError:
        success = False

    save_to_session("success", success)

    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect("/")


@app.route("/register", methods=["POST"])
def register():

    req_username, req_password = request.form["username"], request.form["password"]

    # ================================
    # FEATURE (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is succesful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ================================
    try:
        response = requests.post(
            "http://backend:8000/api/auth/register",
            json={"username": req_username, "password": req_password},
        )

        success = succesful_request(response)
    except requests.exceptions.ConnectionError:
        success = False

    save_to_session("success", success)

    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect("/")


@app.route("/invites", methods=["GET"])
def invites():
    # ==============================
    # FEATURE (list invites)
    #
    # retrieve a list with all events you are invited to and have not yet responded to
    # ==============================

    my_invites = []
    global username

    try:
        response = requests.get(f"http://backend:8000/api/invites?username={username}")
    except requests.exceptions.ConnectionError:
        response = None

    if response is not None and succesful_request(response):
        events = [
            invite["eventId"]
            for invite in response.json()["invites"]
            if invite["status"] == "PENDING"
        ]

        for event in events:
            try:
                response = requests.get(f"http://backend:8000/api/events/{event}")
                if succesful_request(response):
                    event = response.json()["event"]
                    my_invites.append(
                        (
                            event["id"],
                            event["title"],
                            event["date"],
                            event["organizer"],
                            "Public" if event["isPublic"] else "Private",
                        )
                    )
            except requests.exceptions.ConnectionError:
                break  # If server is down, don't continue fetching events

    return render_template(
        "invites.html", username=username, password=password, invites=my_invites
    )


@app.route("/invites", methods=["POST"])
def process_invite():
    if request.json is None or not isinstance(request.json, dict):
        return "Invalid request", 400

    eventId, status = request.json.get("event", None), request.json.get("status", None)

    if not eventId or not status:
        return "Invalid request", 400

    # =======================
    # FEATURE (process invite)
    #
    # process an invite (accept, maybe, don't accept)
    # =======================
    global username
    status = convert_status(status)

    try:
        requests.put(
            "http://backend:8000/api/invites",
            json={"eventId": int(eventId), "username": username, "status": status},
        )
    except requests.exceptions.ConnectionError:
        pass

    return redirect("/invites")


@app.route("/rsvp", methods=["POST"])
def rsvp():
    if request.json is None or not isinstance(request.json, dict):
        return "Invalid request", 400

    eventId, status = request.json.get("event", None), request.json.get("status", None)

    if not eventId or not status:
        return "Invalid request", 400

    # =======================
    # FEATURE (rsvp)
    #
    # rsvp to a public event (accept, maybe, don't accept)
    # =======================
    global username
    status = convert_status(status)

    try:
        # Check if the user received a private invite before rsvp to public event
        response = requests.get(
            f"http://backend:8000/api/invites?eventId={eventId}&username={username}"
        )
    except requests.exceptions.ConnectionError:
        response = None

    # If the user received an invite, update the invite
    if response is not None and succesful_request(response):
        try:
            # If the user received an invite, update the invite
            requests.put(
                "http://backend:8000/api/invites",
                json={"eventId": int(eventId), "username": username, "status": status},
            )
            save_to_session("success", True)
            return redirect("/")
        except requests.exceptions.ConnectionError:
            pass

    # No invite => User is RSVPing to a public event
    # Check if the rsvp exists
    try:
        response = requests.get(
            f"http://backend:8000/api/rsvp?eventId={eventId}&username={username}"
        )
    except requests.exceptions.ConnectionError:
        response = None
    try:
        if response is not None and not succesful_request(response):
            # If it doesn't exist, create it
            requests.post(
                "http://backend:8000/api/rsvp",
                json={"eventId": int(eventId), "username": username, "status": status},
            )
        else:
            # If it does exist, update it
            requests.put(
                "http://backend:8000/api/rsvp",
                json={"eventId": int(eventId), "username": username, "status": status},
            )
    except requests.exceptions.ConnectionError:
        pass

    return redirect("/")


@app.route("/logout")
def logout():
    global username, password

    username = None
    password = None
    return redirect("/")
