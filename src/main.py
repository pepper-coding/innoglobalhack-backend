import uvicorn
from server import app

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.137.1", port=8000)
