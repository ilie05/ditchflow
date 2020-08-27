class Config:
    # SMTP Credentials
    MAIL_SERVER = 'mail.ditchflow.com'
    MAIL_PORT = 25
    MAIL_USERNAME = 'alert@ditchflow.com'
    MAIL_PASSWORD = 'SINCE1937'
    MAIL_SENDER = 'alert@ditchflow.com'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

    SESSION_DURATION = 1  # DAYS. The period duration to stay logged in

    FIELD_NAME = 'Field no. 1'

    BATTERY_MIN_VOLTAGE = 10  # value in Volts
    GO_OFFLINE_TIME = 1800  # value in seconds
    CHECK_FOR_STATUS_TIME = 5  # value in seconds
