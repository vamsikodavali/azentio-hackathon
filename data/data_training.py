
import json

def get_num(d,k):
    try:
        v=d.get(k)
        return None if v is None else float(v)
    except:
        return None

def ratio(a,b):
    if a is None or b is None or b<=0:
        return None
    return round(a/b*100,2)

def bureau_cat(s):
    if s is None:return "Unknown"
    if s>=750:return "Excellent"
    if s>=700:return "Good"
    if s>=650:return "Fair"
    if s>=600:return "Poor"
    return "Very Poor"

def bucket_ratio(r):
    if r is None:return "Unknown"
    if r<20:return "Very Comfortable"
    if r<35:return "Comfortable"
    if r<50:return "Moderate"
    return "High"

def util_cat(r):
    if r is None:return "Unknown"
    if r<30:return "Low"
    if r<70:return "Moderate"
    return "High"

def repayment(curr,maxd):
    curr=curr or 0
    maxd=maxd or 0
    if curr==0 and maxd==0:return "Excellent"
    if curr==0 and maxd<=30:return "Recovered after minor delinquency"
    if curr==0:return "Recovered after historical delinquency"
    if curr<=30:return "Minor delinquency"
    if curr<=60:return "Moderate delinquency"
    return "Severe delinquency"

def analyze(p):
    income=get_num(p,"MONTHLY_INCOME")
    emi=get_num(p,"EMI_AMOUNT")
    sanction=get_num(p,"SANCTION_AMOUNT")
    out=get_num(p,"OUTSTANDING_BALANCE")
    bureau=get_num(p,"BUREAU_SCORE")
    curr=get_num(p,"CURRENT_DPD")
    maxd=get_num(p,"MAX_DPD")
    vintage=get_num(p,"VINTAGE_MONTHS")
    ir=get_num(p,"INTEREST_RATE")

    emi_ratio=ratio(emi,income)
    util=ratio(out,sanction)

    positives=[]; risks=[]; score=0

    if bureau is not None:
        if bureau>=750: score+=3
        elif bureau>=700: score+=2
        elif bureau>=650: score+=1
        else: score-=2
        if bureau>=700: positives.append("Good bureau score")
        else: risks.append("Average/Poor bureau score")

    if emi_ratio is not None:
        if emi_ratio<20: score+=2
        elif emi_ratio<35: score+=1
        elif emi_ratio>50: score-=2
        if emi_ratio<35: positives.append("Comfortable repayment burden")
        elif emi_ratio>50: risks.append("High EMI burden")

    if util is not None:
        if util<30:
            score+=1
            positives.append("Low outstanding exposure")
        elif util>70:
            score-=1
            risks.append("High outstanding exposure")

    if (curr or 0)==0:
        positives.append("No current overdue")
    else:
        score-=2
        risks.append("Current delinquency")

    if (maxd or 0)>=30:
        risks.append(f"Historical delinquency ({int(maxd)} DPD)")

    if vintage is not None and vintage<12:
        risks.append("Limited repayment history")

    if ir is not None and ir>16:
        risks.append("High interest rate")

    if p.get("DEFAULT_FLAG")==1:
        score-=5
        risks.append("Previous default")
    else:
        positives.append("No previous default")

    if p.get("WRITE_OFF_FLAG")==1:
        score-=5
        risks.append("Write-off history")
    else:
        positives.append("No write-off history")

    risk="Low" if score>=5 else "Medium" if score>=2 else "High"
    recommendation={"Low":"Approve","Medium":"Approve with Conditions","High":"Reject"}[risk]

    reasoning={
        "customer_profile":{
            "occupation":p.get("OCCUPATION"),
            "loan_product":p.get("LOAN_PRODUCT"),
            "age":p.get("AGE"),
            "monthly_income":income
        },
        "calculations":{
            # "emi_to_income_ratio":{"value":emi_ratio,"category":bucket_ratio(emi_ratio)},
            "foir":{"value":emi_ratio,"category":bucket_ratio(emi_ratio)},
            "outstanding_utilization":{"value":util,"category":util_cat(util)}
        },
        "credit_analysis":{
            "bureau_score":bureau,
            "bureau_category":bureau_cat(bureau),
            "current_dpd":curr,
            "max_dpd":maxd,
            "repayment_behaviour":repayment(curr,maxd)
        },
        "positive_factors":positives,
        "risk_factors":risks,
        "overall_assessment":f"Overall credit risk assessed as {risk}.",
        "overall_risk":risk
    }
    return reasoning,risk,recommendation

def build_answer(task,reasoning,risk,reco):
    if task=="summary":
        return {"loan_summary":f"Customer is a {risk.lower()}-risk borrower with a {reasoning['credit_analysis']['bureau_category'].lower()} credit profile and {reasoning['calculations']['foir']['category'].lower()} repayment burden."}
    if task=="risk":
        return {"credit_risk":risk}
    return {"recommendation":reco}

TASKS=[
("Generate a loan summary after analysing the customer's financial profile.","summary"),
("Classify the customer's credit risk after analysing the customer's financial profile.","risk"),
("Recommend whether the customer should be approved for a new loan after analysing the customer's financial profile.","recommendation")
]

def create_samples(profile):
    reasoning,risk,reco=analyze(profile)
    samples=[]
    for inst,task in TASKS:
        samples.append({
            "instruction":inst,
            "input":profile,
            "output":{
                "reasoning":reasoning,
                "answer":build_answer(task,reasoning,risk,reco)
            }
        })
    return samples

def main():
    with open("azentio_data_processed.json","r") as f:
        dataset=json.load(f)
    training=[]
    for profile in dataset:
        training.extend(create_samples(profile))
    with open("loan_training.json","w") as f:
        json.dump(training,f,indent=4)
    print(f"Generated {len(training)} training samples.")

if __name__=="__main__":
    main()
