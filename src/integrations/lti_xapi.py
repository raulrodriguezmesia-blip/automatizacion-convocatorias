"""
LTI 1.3 Integration for Convocatorias Platform
Learning Tools Interoperability standard for educational institutions.
"""
import json
import time
import uuid
from typing import Dict, Optional
from urllib.parse import urlencode
import requests
from jose import jwt


class LTIConfig(BaseModel):
    client_id: str
    deployment_id: str
    issuer: str
    auth_url: str
    token_url: str
    jwks_url: str
    private_key: str


class LTIIntegration:
    """
    LTI 1.3 integration for convocatoria creation from LMS.
    
    Enables:
    - Deep linking from LMS to create convocatorias
    - Grade passback for participation tracking
    - Roster sync for attendee lists
    """
    
    def __init__(self, config: LTIConfig):
        self.config = config
    
    def generate_login_url(self, redirect_uri: str, lti_message_hint: str = None) -> str:
        """Generate LTI 1.3 login initiation URL."""
        state = str(uuid.uuid4())
        nonce = str(uuid.uuid4())
        
        params = {
            "iss": self.config.issuer,
            "login_hint": lti_message_hint or str(uuid.uuid4()),
            "target_link_uri": redirect_uri,
            "client_id": self.config.client_id,
            "response_type": "id_token",
            "scope": "openid",
            "nonce": nonce,
            "state": state
        }
        
        return f"{self.config.auth_url}?{urlencode(params)}"
    
    def decode_id_token(self, id_token: str, client_secret: str) -> Dict:
        """Decode and validate LTI ID token."""
        try:
            payload = jwt.decode(
                id_token,
                self.config.jwks_url,
                algorithms=["RS256"],
                audience=self.config.client_id,
                issuer=self.config.issuer
            )
            return payload
        except Exception as e:
            raise ValueError(f"Invalid LTI token: {e}")
    
    def extract_context(self, lti_launch: Dict) -> Dict:
        """Extract course/context from LTI launch."""
        return {
            "course_id": lti_launch.get("https://purl.imsglobal.org/spec/lti/claim/context", {}).get("id"),
            "course_name": lti_launch.get("https://purl.imsglobal.org/spec/lti/claim/context", {}).get("label"),
            "user_email": lti_launch.get("email"),
            "user_name": lti_launch.get("name"),
            "roles": lti_launch.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])
        }
    
    def roster_sync(self, context_id: str, access_token: str) -> List[str]:
        """Sync attendee list from LMS roster."""
        # NUS API call would go here
        # Using access token to fetch roster
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"https://api.lms.com/roster/{context_id}",
            headers=headers
        )
        users = response.json()
        return [user["email"] for user in users if "email" in user]


class XAPIStatement(BaseModel):
    actor: Dict
    verb: Dict
    object: Dict
    timestamp: str
    result: Optional[Dict] = None


class XAPIIntegration:
    """
    xAPI (Experience API) integration for learning analytics.
    
    Tracks convocatoria participation as learning experiences.
    """
    
    def __init__(self, endpoint: str, auth_token: str):
        self.endpoint = endpoint
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def send_statement(self, statement: XAPIStatement) -> bool:
        """Send xAPI statement for convocatoria participation."""
        payload = json.dumps(statement.dict())
        response = requests.post(self.endpoint, data=payload, headers=self.headers)
        return response.status_code == 200
    
    def send_convocatoria_created(self, convocatoria_id: str, organizer_email: str) -> bool:
        statement = XAPIStatement(
            actor={"mbox": f"mailto:{organizer_email}", "name": organizer_email.split("@")[0]},
            verb={"id": "http://adlnet.gov/expapi/verbs/created", "display": {"en-US": "created"}},
            object={"id": f"https://convocatorias.io/convocatorias/{convocatoria_id}", "definition": {"name": {"en-US": "Convocatoria Event"}}},
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        return self.send_statement(statement)
    
    def send_participation(self, convocatoria_id: str, attendee_email: str, attended: bool) -> bool:
        verb_id = "http://adlnet.gov/expapi/verbs/attended" if attended else "http://adlnet.gov/expapi/verbs/absent"
        statement = XAPIStatement(
            actor={"mbox": f"mailto:{attendee_email}"},
            verb={"id": verb_id, "display": {"en-US": "attended" if attended else "absent"}},
            object={"id": f"https://convocatorias.io/convocatorias/{convocatoria_id}"},
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            result={"success": attended}
        )
        return self.send_statement(statement)