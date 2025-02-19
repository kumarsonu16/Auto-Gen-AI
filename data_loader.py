import requests
import xml.etree.ElementTree as ET
from scholarly import scholarly
from autogen import AssistantAgent

class DataLoader:
    def __init__(self, api_key):
        print("DataLoader Init")
        self.groq_api_key = api_key
        self.initialize_search_agent(self.groq_api_key)        
    
    def initialize_search_agent(self, api_key):
        """
        Initializes the search_agent using AutoGen's AssistantAgent.
        """
        self.groq_api_key = api_key
        self.llm_config = {
            'config_list': [
                {
                    'model': 'deepseek-r1-distill-qwen-32b',
                    'api_key': self.groq_api_key,
                    'api_type': 'groq'
                }
            ]
        }

        # Define the system message for the AssistantAgent
        system_message = """
            You are a research assistant. Your task is to suggest 3 related research topics based on the user's query.
            The topics should be concise, relevant, and directly related to the query.
            Return the topics as a bulleted list, one topic per line, in the following format:

            - Topic 1
            - Topic 2
            - Topic 3

            For example:
            If the query is "machine learning," you should return:
            - Deep learning algorithms and applications
            - Reinforcement learning in robotics
            - Natural language processing advancements

            If the query is "climate change," you should return:
            - Impact of climate change on polar ice caps
            - Renewable energy solutions for reducing carbon emissions
            - Role of deforestation in global warming

            Do not include any additional explanations, reasoning, or verbose text. Only return the bulleted list of topics.
            """

        # Initialize the AssistantAgent
        self.search_agent = AssistantAgent(
            name="search_agent",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            code_execution_config=False
        )
        
    
    def extract_related_topics(self, response):
        """
        Extracts the actual related topics from the response.
        """
        # Split the response into lines
        lines = response.split("\n")
        
        # Filter lines that start with a bullet point
        topics = [line.strip() for line in lines if line.strip().startswith("-")]
        return topics
    
    def fetch_arxiv_papers(self, query):
        """
            Fetches top 5 research papers from ArXiv based on the user query.
            If <5 papers are found, expands the search using related topics.
            
            Returns:
                list: A list of dictionaries containing paper details (title, summary, link).
        """
        
        def search_arxiv(query):
            """Helper function to query ArXiv API."""
            url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"
            response = requests.get(url)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                data = [
                    {
                        "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
                        "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text,
                        "link": entry.find("{http://www.w3.org/2005/Atom}id").text
                    }
                    for entry in root.findall("{http://www.w3.org/2005/Atom}entry")
                ]
                return data
            return []

        papers = search_arxiv(query)

        if len(papers) < 5 and self.search_agent:  # If fewer than 5 papers, expand search
            related_topics_response = self.search_agent.generate_reply(
                messages=[{"role": "user", "content": f"Suggest 3 related research topics for '{query}'"}]
            )
            # related_topics = related_topics_response.get("content", "").split("\n")
            # Extract the actual topics from the verbose response
            related_topics = self.extract_related_topics(related_topics_response.get("content", ""))

            for topic in related_topics:
                topic = topic.strip()
                if topic and len(papers) < 5:
                    new_papers = search_arxiv(topic)
                    papers.extend(new_papers)
                    papers = papers[:5]  # Ensure max 5 papers            
        return papers

    def fetch_google_scholar_papers(self, query):
        """
            Fetches top 5 research papers from Google Scholar.
            Returns:
                list: A list of dictionaries containing paper details (title, summary, link)
        """
        papers = []
        search_results = scholarly.search_pubs(query)

        for i, paper in enumerate(search_results):
            if i >= 5:
                break
            papers.append({
                "title": paper["bib"]["title"],
                "summary": paper["bib"].get("abstract", "No summary available"),
                "link": paper.get("pub_url", "No link available")
            })
        return papers
