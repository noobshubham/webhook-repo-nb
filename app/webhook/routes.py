from flask import jsonify, request
from datetime import datetime, timezone
from app.webhook import webhook
from app.extensions import mongo

# ------------------
# Helpers
# ------------------

def get_utc_time():
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()

def save_event(data):
    """Insert event if not duplicate."""
    collection = mongo.db.events

    # Prevent duplicate using request_id
    if collection.find_one({"request_id": data["request_id"]}):
        return
    
    collection.insert_one(data)

@webhook.route("/")
def home():
    return "The Flask API is UP! Maintained and Developed by SHUBHAM."

# ------------------
# Webhook Receiver
# ------------------

@webhook.route('/webhook', methods=["POST"])
def github_webhook():

    event_type = request.headers.get("X-GitHub-Event")
    payload = request.json

    if not payload:
        return jsonify({"error": "Invalid payload"}), 400
    
    try:
        # PUSH
        if event_type == "push":
            data = {
                "request_id": payload["head_commit"]["id"],
                "author": payload["pusher"]["name"],
                "action": "PUSH",
                "from_branch": None,
                "to_branch": payload["ref"].split("/")[-1],
                "timestamp": payload["head_commit"]["timestamp"]
            }
            save_event(data)

        # PR
        elif event_type == "pull_request":

            pr = payload["pull_request"]
            pr_action = payload["action"]

            is_merged = pr_action == "closed" and pr["merged"] is True

            action = "MERGE" if is_merged else "PULL_REQUEST"

            data = {
                "request_id": str(pr["id"]),
                "author": pr["user"]["login"],
                "action": action,
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": pr["merged_at"] if is_merged else pr["created_at"]
            }

            save_event(data)
        
        else:
            return jsonify({"message": "Event Ignored"}), 200
        
        return jsonify({"message": "Event Stored"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------
# Fetch Events (For UI)
# ------------------

@webhook.route("/events", methods=["GET"])
def get_events():
    since = request.args.get("since")
    query = {}
    if since:
        query["timestamp"] = {"$gt": since}

    events = list(
        mongo.db.events.find(query, {"_id": 0}).sort("timestamp", -1).limit(20)
    )

    return jsonify(events)
