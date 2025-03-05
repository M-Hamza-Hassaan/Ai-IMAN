# Intelligent Mesh Ai Network 🌍

## Problem Statement
Students, especially in remote areas, struggle to access relevant educational resources due to poor infrastructure and limited connectivity. Many educational institutions lack efficient ways to route queries and provide real-time information based on geospatial data.

## Our Solution
We developed an **Intelligent mesh ai network** that enables students and educators to interact with an intelligent system capable of routing queries efficiently. By leveraging geospatial datasets and AI, we can process user queries and dynamically route them to the nearest educational institution, providing real-time responses and visualization.

---
![image](https://github.com/user-attachments/assets/84707bba-b87d-424c-80bc-24562b5b7088)

---

## Technologies Used
- **Streamlit**: For the web-based interactive UI
- **Folium**: For geospatial visualization
- **Pandas & GeoPandas**: For data processing and manipulation
- **SciPy KDTree**: For efficient nearest-school lookup
- **Bagoodex AI API**: For AI-powered query processing
- **Shapely**: For geospatial computations
- **NumPy**: For numerical computations

## Process Pipeline
1. **User Query Input**: The user enters a question related to education.
2. **Location-Based Processing**: The system takes latitude and longitude as input.
3. **AI Query Processing**: The AI model processes the query and determines the best-matching response.
4. **Geospatial Routing**: The system finds the nearest educational institution to route the query.
5. **Network Visualization**: The system displays an interactive map with all available institutions and highlights the selected one.
6. **Response Generation**: The AI model returns a relevant response based on location and query context.

## How It Works
1. The user inputs a query and location (latitude & longitude).
2. The AI processes the query and routes it to the nearest institution.
3. The nearest institution is determined using **KDTree** for fast geospatial lookup.
4. The interactive map displays available institutions, marking the selected one.
5. The AI returns an appropriate response, simulating a real-world query-routing system.

## Getting Started
1. Clone the repository:
   ```sh
   git clone https://github.com/M-Hamza-Hassaan/Connect-Ai-Innovators.git
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   streamlit run app.py
   ```

## Future Enhancements
- Implement real-time data updates from live educational databases.
- Integrate a chatbot to handle dynamic queries more efficiently.
- Expand dataset coverage for global educational institutions.
- Improve AI models for better response accuracy.

## Contributors
- **[Muhammad Hamza Hassaan](https://www.linkedin.com/in/muhammad-hamza-hassaan-29920a25a/)** - Project Lead

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

