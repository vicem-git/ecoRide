from pydantic import ValidationError

VALIDATION_MESSAGES = {
    "start_city": "Veuillez choisir une ville de départ.",
    "end_city": "Veuillez choisir une ville d'arrivée.",
    "start_datetime": "Veuillez entrer une date valide.",
    "price": "Veuillez entrer un prix valide.",
    "vehicle_id": "Veuillez sélectionner un véhicule.",
    "email": "Veuillez fournir une adresse e-mail valide.",
    "password": "Le mot de passe doit contenir au moins 8 caractères",
}


def render_pydantic_errors(e: ValidationError):
    output = []
    for err in e.errors():
        loc = err["loc"][0]
        # PYDANTIC UGLY ERRORS
        if loc == "__root__":
            msg = err["msg"]
        # MY ERRORS
        else:
            msg = VALIDATION_MESSAGES.get(loc, err["msg"])
        output.append(msg)
    return output if output else "Erreur de validation inconnue."
