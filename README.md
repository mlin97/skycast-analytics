# 🌤️ SkyCast Analytics

SkyCast Analytics is a sleek, modern Streamlit dashboard that allows you to compare historical temperature trends between any two cities in the world. Built with Python and powered by the Open-Meteo API, it features a premium UI, interactive charts, and robust error handling.

## ✨ Features

-   **City Comparison**: Side-by-side search for any two cities (e.g., "New York" vs "London").
-   **Historical Data**: Analyze daily maximum temperatures for the past 30 days (customizable date range).
-   **Interactive Visualizations**:
    -   Dynamic Line Chart (Neon Blue & Sunset Orange palette).
    -   Auto-expanding charts for immediate insights.
    -   "Dataset Overview" metrics showing average temperatures.
-   **Robust Error Handling**: Explicit feedback for loading states and timeouts.
-   **Responsive Design**: Mobile-friendly layout with "Light Mode" optimization.

## 🛠️ Tech Stack

-   **Python 3.10+**
-   **Streamlit**: For the web application framework.
-   **Pandas**: For data manipulation.
-   **Plotly Express**: For interactive charting.
-   **Requests**: For API consumption.
-   **Open-Meteo API**: Free Weather API for historical data.

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed on your system.

### Installation

1.  Clone the repository (if applicable) or navigate to the project folder:
    ```bash
    cd weather-vibe-dash
    ```

2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the App

Run the Streamlit application:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## ☁️ Deployment

This app is optimized for **Streamlit Community Cloud**.

1.  Push your code to a GitHub repository.
2.  Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3.  Click "New app" and select your repository.
4.  Click **Deploy!**

## 📂 Project Structure

-   `app.py`: Main application logic.
-   `requirements.txt`: Python dependencies.
-   `Dockerfile`: (Optional) For containerized deployment.
