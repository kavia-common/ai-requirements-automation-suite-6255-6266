from app import get_app

app = get_app()

if __name__ == "__main__":
    # Bind to 0.0.0.0:3001 by default for containerized envs
    app.run(host="0.0.0.0", port=3001)
