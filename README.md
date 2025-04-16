# 👕 TeeShirts Inventory Management System

Welcome to the **TeeShirts Inventory Management System**, a modern, interactive Streamlit-based web application designed to help small-to-medium retail businesses efficiently manage, visualize, and analyze their t-shirt inventory.

## 🚀 Features

- **Browse Inventory**
  - Filter by brand, color, size, price range, and discount
  - Interactive charts (Altair) for breakdowns by brand, size, or color
  - Modern product card display with pagination and discount highlights

- **Ask Questions**
  - Natural language interface powered by LLM (LLaMA 3 via Groq)
  - Supports analytical queries like:
    - *"How many red t-shirts are in stock?"*
    - *"What's the average price of Nike t-shirts?"*
    - *"Which brand has the most t-shirts?"*

- **Smart SQL Generation**
  - Uses LangChain + Few-Shot Learning to dynamically generate SQL queries and return clean insights

- **Stylish UI**
  - Custom CSS for a modern, mobile-friendly layout
  - Metrics, badges, and cards to enhance user experience

---

## 🧰 Tech Stack

| Component     | Description                                    |
|---------------|------------------------------------------------|
| **Streamlit** | Web UI framework for quick dashboards          |
| **LangChain** | LLM-based orchestration for SQL question answering |
| **Groq + LLaMA 3** | High-performance LLM inference             |
| **MySQL**     | Backend relational database for inventory data |
| **Altair**    | Declarative charting library for visualizations |
| **ChromaDB**  | Semantic search for few-shot example selection |
| **HuggingFace Embeddings** | Used for semantic similarity        |

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/teeshirts-inventory-app.git
cd teeshirts-inventory-app
```

### 2. Install Dependencies

It's recommended to use a virtual environment:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:

```
streamlit
langchain
langchain-community
langchain-experimental
langchain-groq
mysql-connector-python
sqlalchemy
python-dotenv
pymysql
altair
pandas
```

### 3. Set Up `.env` File

Create a `.env` file in the root directory to store your keys

### 4. Set Up MySQL Database

Make sure you have a MySQL server running. Make use of the atliq_tshirts.sql file.


### 5. Run the App

```bash
streamlit run main.py
```

---

## 📁 Project Structure

```bash
.
├── main.py                   # Main Streamlit application
├── langchain_helper.py       # LangChain integration and prompt engineering
├── few_shots.py              # Few-shot examples for better LLM responses
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 💡 Sample Questions You Can Ask

- "How many XL size t-shirts do we have?"
- "How much revenue will we generate selling all discounted Levi’s?"
- "What's the total inventory value?"

---


## 🧠 Credits

- Built with 💙 by [Your Name / Team]
- Powered by [Streamlit](https://streamlit.io/) and [LangChain](https://www.langchain.com/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙋‍♀️ Contributions

Pull requests and suggestions are welcome! If you'd like to contribute, please fork the repo and submit a PR.

```
