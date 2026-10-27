Data sent from clients to server should look like this

{
    "action": "whisper" // message, login, logout etc
    "data": "hej hej"
}


Data sent from server to clients should look like this

{
    "action": "message" // message, auth_status
    "data": "" // login_response_success, logout_response_failed, message sender and text, etc
}