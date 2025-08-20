import os
import firebase_admin
from firebase_admin import firestore
from google.auth.credentials import AnonymousCredentials

def init_firestore():
    project_id = os.getenv("GCLOUD_PROJECT")

    if firebase_admin._apps:
        return firestore.client()

    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        print(f"Firestore en mode émulateur ({os.environ['FIRESTORE_EMULATOR_HOST']})")
        cred = AnonymousCredentials()
        firebase_admin.initialize_app(
            credential=cred,
            options={"projectId": project_id}
        )

    return firestore.client()
