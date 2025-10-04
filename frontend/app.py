import streamlit as st
import requests

st.title("Find your data")

user_query = st.text_input("Enter your natural language query:")

if st.button("Genetrate Query"):
    response = requests.post("http://localhost:8000/query", json={"query": user_query})
    result = response.json()
    st.subheader("Generated MongoDB Query")
    st.code(result.get("mongo_query", ""), language="json")
    if "results" in result:
        st.subheader("Query Results")
        st.write(result["results"])
    elif "count" in result:
        st.subheader("Count Result")
        st.write(result["count"])
    elif "error" in result:
        st.error(result["error"])