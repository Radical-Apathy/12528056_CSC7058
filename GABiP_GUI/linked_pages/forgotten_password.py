import streamlit as st 


title_style = '<p style="font-family:sans-serif; color:Green; font-size: 42px;"><strong>Password Reset</strong></p>'


st.title("Password Reset :lizard:")
st.markdown(title_style, unsafe_allow_html=True) 
st.title(':lizard: :frog:')

with st.form("password_reset"):
   st.write("Please enter new password - must be a minimum of 8 characters. Must contain at least one uppercase and one special character")
   newPassword =st.text_input("New Password", type='password')
   reTypePassword =st.text_input("Re-type Password", type='password')
   
   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
        if newPassword =="" or reTypePassword=="":
         st.write("Fields can not be left blank") 
        if newPassword != reTypePassword:
         st.write("Fields must match") 
        
         #st.write(newPassword, reTypePassword)
        if newPassword==reTypePassword and newPassword!="" and reTypePassword!="":
            st.success("Thank you! Please click HERE to return to login page and sign in with new password")

    
