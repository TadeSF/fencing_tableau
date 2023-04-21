from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from fencer import Fencer
import os
import requests
from requests.exceptions import ConnectionError, HTTPError
import logging
from dotenv import load_dotenv

# ------- Load Environment Variables -------
load_dotenv()
EXPO_API_KEY = os.getenv("EXPO_API_KEY")



# ------- Logging -------
try:  # Error Catch for Sphinx Documentation
    # create logger
    logger = logging.getLogger('fencer')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create file handler and set level to debug
    fh = logging.FileHandler('logs/tournament.log')
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

except FileNotFoundError:
    pass

# ------- General Notification -------
def send_push_message(token: str, message: str, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        logger.error(exc.errors)
        logger.error(exc.message)
        # Response is likely a `dict` with 'errors' key.
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        logger.error(exc)
        raise self.retry(exc=exc)
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        logger.error("Device not registered")
    except PushTicketError:
        # Mark the ticket as invalid
        logger.error("Push ticket error")
    except Exception as exc:
        # Encountered some other error during the request, it is important to
        # catch all exceptions here so that the outer for loop doesn't break.
        logger.error(exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception flows.
        response.validate_response()
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        logger.error(exc.errors)
        logger.error(exc.message)
        # Response is likely a `dict` with 'errors' key.
        raise self.retry(exc=exc)
    except Exception as exc:
        # Encountered some other formatting or server error.
        logger.error(exc)

def send_fencer_push_message(fencer: Fencer, message: str, extra=None):
    if len(fencer.push_notification_tokens) == 0:
        raise ValueError("Fencer has no push notification tokens")
    
    if extra is None:
        extra = {
            "type": "general",
            "fencer_id": fencer.id,
        }
    else:
        extra["type"] = "type" if "type" not in extra else extra["type"]
        extra["fencer_id"] = fencer.id
    
    for token in fencer.push_notification_tokens:
        send_push_message(token, message, extra)


# ------- Custom Fencer Notifications -------
def get_ready_notification(fencer: Fencer, against: Fencer, piste):
    message = f"Get ready to fence {against.name} on piste {piste}"
    extra = {
        "type": "get_ready",
        "fencer_id": fencer.id,
        "against_id": against.id,
        "piste": piste,
    }
    send_fencer_push_message(fencer, message, extra)

def start_match_notification(fencer: Fencer, against: Fencer, piste):
    message = f"Match against {against.name} on piste {piste} is starting"
    extra = {
        "type": "start_match",
        "fencer_id": fencer.id,
        "against_id": against.id,
        "piste": piste,
    }
    send_fencer_push_message(fencer, message, extra)

def tournament_message_notification(fencer: Fencer, message: str):
    extra = {
        "type": "tournament_message",
        "fencer_id": fencer.id,
    }
    send_fencer_push_message(fencer, message, extra)
