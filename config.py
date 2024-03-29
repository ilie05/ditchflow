class Config:
    SECRET_KEY = '49tZyjJmZxiQbL22EtSVtLY1WGEnEBH7'

    # SMTP Credentials
    MAIL_SERVER = 'mail.ditchflow.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'alerts@ditchflow.com'
    MAIL_PASSWORD = 'Gpba17@5'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

    SESSION_DURATION = 1  # DAYS. The period duration to stay logged in

    BATTERY_MIN_VOLTAGE = 10  # value in Volts
    WATER_MAX_LEVEL = 21.5
    GO_OFFLINE_SENSOR_TIME = 1800  # value in seconds
    GO_OFFLINE_VALVE_TIME = 600  # value in seconds
    CHECK_FOR_STATUS_TIME = 10  # value in seconds

    # device settings
    DEVICE_PORT = "/dev/ttyAMA0"
    BAUD_RATE = 9600

    SYSTEM_BATTERY_MIN_VOLTAGE = 11  # value in Volts
    SYSTEM_CPU_MAX_TEMPERATURE = 180  # value in F degree
    MAIN_SYSTEM_DEVICE_PORT = "/dev/ttyAMA1"

    PING_INTERVAL = 15  # min

    # MOVING VALVES VALIDATION TIME
    MOVING_TIME = 6  # sec.
    IDLE_TIME = 30  # sec.

    ADMIN_USER = False  # True / False

    # GPS
    GPS_SERIAL_PORT = '/dev/ttyACM0'
    GROUND_SPEED_MIN = 10  # Knots
    
    #SMS
    TELNYX_KEY = "KEY017A21C91A0D683DFD31F56D74AF9DA5_5I19OMvMi2eTVWTvuPkcqQ"
    TELNYX_NUMBER = "+17602549901"