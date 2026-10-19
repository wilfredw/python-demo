import uvicorn


def main() -> None:
    """Run the development server using the package-qualified ASGI target."""
    uvicorn.run("fastapi_app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
