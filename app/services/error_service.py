from flask import jsonify


def generate_error(logger, message, code=400):
    logger.debug(message)
    return jsonify({ "error": message }), code