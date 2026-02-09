# 🦅 Competitor Price Intelligence API

A powerful, automated market intelligence system that tracks competitor prices, analyzes trends, and provides actionable insights via a robust REST API.

Built with **FastAPI**, **MongoDB**, and **Docker**. Designed for autonomous operation on cloud platforms like **Render**.

---

## 🚀 Key Features

- **Automated Scraping**: Runs daily at 03:00 AM (via APScheduler) to fetch fresh data from competitors.
- **Competitor Analysis**: Automatically matches products across sites (Rugs Direct, Debenhams, Love Rugs) and calculates price differences.
- **Price History**: Tracks historical pricing data for every product to visualize trends over time.
- **Robust API**: comprehensive endpoints for retrieving products, searching, filtering, and accessing history.
- **Cloud-Native**: Dockerized application ready for deployment on Render, AWS, or DigitalOcean.
- **Secure**: API Key authentication protects your data.

---

## 🛠️ Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (High-performance Python API)
- **Database**: [MongoDB Atlas](https://www.mongodb.com/atlas) (Cloud NoSQL Database)
- **Task Scheduling**: [APScheduler](https://apscheduler.readthedocs.io/) (Background jobs)
- **Scraping**: Python `requests`, `BeautifulSoup`, `lxml`
- **Deployment**: Docker & Gunicorn

---

## 🔌 API Endpoints

| Method | Endpoint            | Description                                                                                       |
| :----- | :------------------ | :------------------------------------------------------------------------------------------------ |
| `GET`  | `/api/products`     | Retrieve paginated list of products with competitor analysis. Supports `search`, `page`, `limit`. |
| `GET`  | `/api/history/{id}` | Get historical price data for a specific product.                                                 |
| `POST` | `/api/scrape`       | Trigger an immediate scrape job manually.                                                         |
| `GET`  | `/health`           | Health check endpoint for monitoring.                                                             |

> **Note:** All protected endpoints require the `X-API-Key` header.

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.12+
- MongoDB Atlas Account

### Local Development

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/ohhamamcioglu/scrapeApp.git
    cd scrapeApp
    ```

2.  **Create Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory:

    ```ini
    MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
    API_KEY=your-secret-key-12345
    ```

5.  **Run the Server:**
    ```bash
    uvicorn main:app --reload
    ```
    Access the API documentation at `http://localhost:8000/docs`.

### 🐳 Docker Deployment

1.  **Build the Image:**

    ```bash
    docker build -t scrape-app .
    ```

2.  **Run the Container:**
    ```bash
    docker run -p 8000:8000 --env-file .env scrape-app
    ```

---

## ☁️ Deployment on Render.com

1.  **Push** this repository to GitHub.
2.  Create a new **Web Service** on Render.
3.  Connect your repository.
4.  **Settings:**
    - **Runtime:** Python 3
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `./start.sh`
5.  **Environment Variables:** Add `MONGO_URI` and `API_KEY`.

That's it! Your autonomous price tracker is live. 🚀
