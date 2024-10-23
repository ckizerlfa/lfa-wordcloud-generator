import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import re
from collections import Counter

# Download only stopwords
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('stopwords')
    except Exception as e:
        st.error(f"Error downloading NLTK data: {str(e)}")
        return False
    return True

def simple_tokenize(text):
    """Simple word tokenization using regex."""
    # Split on whitespace and remove empty strings
    return [word.strip() for word in re.findall(r'\b\w+\b', text.lower()) if word.strip()]

def clean_text(text):
    """Clean and preprocess text for word cloud generation."""
    if pd.isna(text):
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    try:
        # Use simple tokenization
        tokens = simple_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        
        return ' '.join(tokens)
    except Exception as e:
        st.error(f"Error in text cleaning: {str(e)}")
        return text

def main():
    st.title("Article Word Cloud Generator")
    
    # Download NLTK stopwords at startup
    with st.spinner("Downloading required NLTK data..."):
        if not download_nltk_data():
            st.error("Failed to download required NLTK data. Please try again.")
            return
    
    # File upload
    st.write("Upload a spreadsheet containing full articles in a single column")
    uploaded_file = st.file_uploader("Choose a file", type=['xlsx', 'csv'])
    
    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Verify there's only one column
            if len(df.columns) != 1:
                st.error("Please upload a spreadsheet with exactly one column containing the articles.")
                return
            
            # Sidebar controls
            st.sidebar.header("Word Cloud Settings")
            
            max_words = st.sidebar.slider("Maximum number of words", 50, 500, 200)
            width = st.sidebar.slider("Width", 400, 2000, 800)
            height = st.sidebar.slider("Height", 400, 2000, 400)
            background_color = st.sidebar.color_picker("Background color", "#ffffff")
            
            # Combine all articles and clean the text
            all_text = ' '.join(df[df.columns[0]].apply(clean_text))
            
            if not all_text.strip():
                st.error("No valid text found in the uploaded file after cleaning.")
                return
            
            # Generate word cloud
            wordcloud = WordCloud(
                width=width,
                height=height,
                background_color=background_color,
                max_words=max_words,
                contour_width=1,
                contour_color='steelblue'
            ).generate(all_text)
            
            # Clear any existing plots
            plt.clf()
            
            # Create a new figure with specified DPI
            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
            
            # Display the word cloud
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            
            # Add padding to prevent cutoff
            plt.tight_layout(pad=0)
            
            # Use Streamlit's pyplot with the figure
            st.pyplot(fig)
            
            # Add download button for the word cloud
            if st.button("Download Word Cloud"):
                wordcloud.to_file("wordcloud.png")
                st.success("Word cloud has been saved as 'wordcloud.png'")
            
            # Create a word frequency table
            word_list = all_text.split()
            word_freq = Counter(word_list)
            word_freq_df = pd.DataFrame(list(word_freq.items()), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False).reset_index(drop=True)
            
            # Display the word frequency table
            st.write("### Word Frequency Table")
            st.dataframe(word_freq_df, width=1000, height=600)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Full error details:")
            st.exception(e)

if __name__ == "__main__":
    main()
