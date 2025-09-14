import pandas as pd #type:ignore
import os
import re

df=pd.read_csv("jobs_data.csv")
print(df.shape)
print(df.head())

df=df.drop_duplicates()

df=df.dropna(subset=["Title","Location"])
df=df.fillna("Not Mentioned")

df["Title"]=df["Title"].str.strip()
df["Company"]=df["Company"].str.strip()
df["Location"]=df["Location"].str.strip()

df["Location"] = df["Location"].replace({"Bangalore": "Bengaluru","Bangalore Rural": "Bengaluru",
                                         "Bengaluru(Whitefield)": "Bengaluru","Bengaluru(HSR Layout)": "Bengaluru",
                                         "Bengaluru(Mahadevpura)": "Bengaluru","Bengaluru(Bannerghatta Road)": "Bengaluru",
                                         "Mumbai (All Areas)": "Mumbai","Mumbai Suburban, Goregaon": "Mumbai",
                                         "Navi Mumbai, Mumbai (All Areas)": "Mumbai","Gurugram, Mumbai (All Areas)": "Mumbai",
                                         "New Delhi(Rithala)": "New Delhi","Delhi / NCR": "Delhi NCR","Noida, Delhi / NCR": "Delhi NCR",
                                         "New Delhi, Faridabad, Delhi / NCR": "Delhi NCR","Noida(Sector 1)": "Noida",
                                         "Kolkata(Taratala)": "Kolkata","Pune(Pune International Airport Area)": "Pune",
                                         "Pune, Bengaluru": "Hybrid","Hyderabad, Pune, Gurugram, Bengaluru": "Hybrid",
                                         "Kolkata, Hyderabad, Pune": "Hybrid","Mumbai, Pune, Chennai": "Hybrid",
                                         "Mumbai, Pune(Pune International Airport Area)": "Hybrid","Mumbai, Bengaluru, Delhi / NCR": "Hybrid",
                                         "Mumbai, Delhi / NCR, Bengaluru": "Hybrid","Hyderabad, Gurugram, Bengaluru": "Hybrid",
                                         "Hyderabad, Pune, Gurugram, Bengaluru": "Hybrid","Ahmedabad, Gurugram, Bengaluru": "Hybrid",
                                         "Noida, Chennai, Bengaluru": "Hybrid","Pune, Chennai, Mumbai (All Areas)": "Hybrid",
                                         "Indore, Pune, Bengaluru": "Hybrid","Gurugram, Coimbatore, Bengaluru": "Hybrid",
                                         "New Delhi, Nairobi": "Hybrid","New Delhi, Faridabad, Delhi / NCR": "Hybrid",
                                         "Hybrid - Pune, Bengaluru, Mumbai (All Areas)": "Hybrid","Hybrid - Pune, Gurugram, Bengaluru": "Hybrid",
                                         "Hybrid - Hyderabad": "Hybrid","Hybrid - Hyderabad, Chennai, Bengaluru": "Hybrid",
                                         "Hybrid - Noida, Gurugram, Delhi / NCR": "Hybrid","Hybrid - Noida, Pune, Bengaluru": "Hybrid",
                                         "Hybrid - Pune, Mumbai (All Areas)": "Hybrid","Hybrid - Gurugram": "Hybrid","Hybrid - Kochi": "Hybrid",
                                         "Atpadi, Vellore": "Hybrid","Bhubaneswar, Cuttack, Rourkela": "Hybrid", "Hyderabad, Gurugram":"Hybrid",
                                         "Kolkata, Mumbai, New Delhi, Hyderabad, Pune, Chennai, Bengaluru":"Hybrid"})

df["Company"]=df["Company"].str.replace(r"(?i)posted by","", regex=True).str.strip() # ?i->case-insensitive

# parse experience
def parse_exp(exp):
    if pd.isna(exp) or exp in ["Not Mentioned", ""]:
        return(None, None)
    nums=re.findall(r"\d+", exp)
    if len(nums)==2:
        return int(nums[0]),int(nums[1])
    elif len(nums)==1:
        return int(nums[0]),int(nums[0])
    return(None,None)

df[["Min Experience","Max Experience"]]=df["Experience"].apply(lambda x:pd.Series(parse_exp(x)))


df["Title"]=df["Title"].replace({"Machine Learning Engineer":"ML Engineer",
                                "Artificial Intelligence Engineer":"AI Engineer",
                                "Data Analyst,Data Scientist":"Miscellaneous", "Data Scientist,AI Engineer":"Miscellaneous",
                                "Data Analyst,Data Engineer":"Miscellaneous"})

# detect roles
roles_list=["Data Analyst","Data Engineer", "Data Scientist", "ML Engineer", "AI Engineer"]

def detect_roles(title):
    found=[role for role in roles_list
           if role.lower() in str(title).lower()]
    return ",".join(found) if found else "Miscellaneous"

df["Job Roles"]=df["Title"].apply(detect_roles)

df["Company"] = df["Company"].str.replace(r"\b(Pvt(\.?)|Private)\s+(Ltd|Limited)\b", "", 
                                          regex=True, flags=re.IGNORECASE).str.strip()

df["Job Roles"]=df["Job Roles"].replace({"Machine Learning Engineer":"ML Engineer",
                                "Artificial Intelligence Engineer":"AI Engineer",
                                "Data Analyst,Data Scientist":"Miscellaneous", "Data Scientist,AI Engineer":"Miscellaneous",
                                "Data Analyst,Data Engineer":"Miscellaneous"})

keep_columns=["Title","Job Roles","Company","Location","Min Experience","Max Experience","Posted"]
df=df[keep_columns]

out_csv="clean_jobs.csv"
df.to_csv(out_csv, index=False, encoding="utf-8-sig")
print(f"Cleaned data saved to {out_csv}, total_rows={len(df)}")
