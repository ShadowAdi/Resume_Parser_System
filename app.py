import streamlit as st
import nltk
import re
import pickle
import base64
import os
from streamlit_tags import st_tags
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
import time


nltk.download("punkt")
nltk.download("stopwords")


with open("./pklFiles/tfidf.pkl", "rb") as file:
    tfidfVectorizer = pickle.load(file)


with open("./pklFiles/model.pkl", "rb") as file:
    model = pickle.load(file)

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def cleanResume(txt):
    cleanText = re.sub('http\S+\s', ' ', txt)
    cleanText = re.sub('RT|cc', ' ', cleanText)
    cleanText = re.sub('#\S+\s', ' ', cleanText)
    cleanText = re.sub('@\S+', '  ', cleanText)
    cleanText = re.sub('[%s]' % re.escape(
        """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
    cleanText = re.sub('\s+', ' ', cleanText)
    return cleanText


st.title("Resume Screening App")
pdf_file = st.file_uploader("Upload Your Resume", type=["pdf", "txt"])
if pdf_file is not None:
    with open("temp_resume.pdf", "wb") as f:
        f.write(pdf_file.getvalue())
    
    show_pdf("temp_resume.pdf")

    st.divider()

    resume_data = ResumeParser("temp_resume.pdf").get_extracted_data()
    resume_text=pdf_reader("temp_resume.pdf")


    st.header("**Resume Analysis**")
    st.success("Hello "+ resume_data['name'])
    st.subheader("**Your Basic info**")
    print(resume_data['total_experience'])
    try:
        st.text('Name: '+resume_data['name'])
        st.text('Email: ' + resume_data['email'])
        st.text('Contact: ' + resume_data['mobile_number'])
        st.text('Years Of Experience: ' + resume_data['total_experience'])
        st.text('Resume pages: '+str(resume_data['no_of_pages']))

    
        
    except:
        pass
    st.divider()

    num_skills = len(resume_data['skills'])
    num_columns = 3
    skills_per_column = num_skills // num_columns

    st.subheader("Your Skills")

    col1, col2, col3 = st.columns(3)

    for i, skill in enumerate(resume_data['skills']):
        if i < skills_per_column:
            with col1:
                st.text(skill)
        elif i < 2 * skills_per_column:
            with col2:
                st.text(skill)
        else:
        
            with col3:
                st.text(skill)

    st.divider()

    cand_level = ''
    if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
    elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
    elif resume_data['no_of_pages'] >=3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)


    st.subheader("**Resume Tips & Ideas💡**")
    resume_score = 0
    if 'Objective' in resume_text:
                    resume_score = resume_score+20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',unsafe_allow_html=True)
    else:
                    st.markdown('''<h5 style='text-align: left; color: #dadada;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

    if 'Declaration'  in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration/h4>''',unsafe_allow_html=True)
    else:
                    st.markdown('''<h5 style='text-align: left; color: #dadada;'>[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',unsafe_allow_html=True)

    if 'Hobbies' or 'Interests'in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
    else:
        st.markdown('''<h5 style='text-align: left; color: #dadada;'>[-] Please add Hobbies. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

    if 'Achievements' in resume_text:
        resume_score = resume_score + 20
        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
    else:
        st.markdown('''<h5 style='text-align: left; color: #dadada;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

    if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
    else:
                    st.markdown('''<h5 style='text-align: left; color: #dadada;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

    st.subheader("**Resume Score📝**")
    st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
    my_bar = st.progress(0)
    score = 0
    for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
    st.success('** Your Resume Writing Score: ' + str(score)+'**')
    st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")
    st.balloons()
    st.divider()


    


    try:
        resume_bytes = pdf_file.read()
        resume_text = resume_bytes.decode("utf-8")
    except UnicodeDecodeError:
        resume_text = resume_bytes.decode('latin-1')
    cleaned_resume = cleanResume(resume_text)
    input_features = tfidfVectorizer.transform([cleaned_resume])
    prediction_id = model.predict(input_features)[0]
    category_mapping = {'Data Science': 6,
                        'HR': 12,
                        'Advocate': 0,
                        'Arts': 1,
                        'Web Designing': 24,
                        'Mechanical Engineer': 16,
                        'Sales': 22,
                        'Health and fitness': 14,
                        'Civil Engineer': 5,
                        'Java Developer': 15,
                        'Business Analyst': 4,
                        'SAP Developer': 21,
                        'Automation Testing': 2,
                        'Electrical Engineering': 11,
                        'Operations Manager': 18,
                        'Python Developer': 20,
                        'DevOps Engineer': 8,
                        'Network Security Engineer': 17,
                        'PMO': 19,
                        'Database': 7,
                        'Hadoop': 13,
                        'ETL Developer': 10,
                        'DotNet Developer': 9,
                        'Blockchain': 3,
                        'Testing': 23}
    for i, val in category_mapping.items():
        if val == prediction_id:
            st.subheader("Model Prediction")
            st.success(f"A/C To My Model You Are Into {i}")
            st.warning("** Note: My Model is Not 100% Accuracte...So It Can Happen You see Wrong Prediction **")



    # Delete the temporary PDF file
    os.remove("temp_resume.pdf")
