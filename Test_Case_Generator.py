import pandas as pd
from helper_main import *
from openpyxl import Workbook
from io import BytesIO

st.title("Intelligent Test Case Generator")

requirement_document = st.file_uploader("Upload requirement document in .csv file")

requirements={}
requirement_count = 0

if requirement_document is not None:
    dataframe = pd.read_csv(requirement_document, encoding='latin1')
    requirements = dataframe.to_dict(orient='records')

# st.sidebar.page_link("Test_Case_Generator.py")
# st.sidebar.page_link("pages/document_upload.py")

def create_excel(test_cases):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Test Cases"

    # Define headers
    headers = ["Test Case ID", "Objective", "Requirement Covered", "Test Design Technique", "Pre-conditions", "Post-condition",
               "Steps to Execute", "Expected Results"]
    sheet.append(headers)

    # Iterate through the test cases
    for item in test_cases:
        requirement_covered = item.get("Requirement Covered", "N/A")  # Default to "N/A" if key is missing
        buffer_testcase = item.get("Test Cases", "")

        for set_of_cases in buffer_testcase:
            #for case in set_of_cases:
                # Parse details
            lines = [line.strip() for line in set_of_cases.split("\n") if line.strip()]
            test_case_id = next(
                (line.split(":", 1)[1].strip() for line in lines if line.startswith("Test Case ID")), "N/A")
            objective = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("Objective")),
                             "N/A")
            design_technique = next(
                (line.split(":", 1)[1].strip() for line in lines if line.startswith("Test Design Technique")),
                "N/A")
            pre_conditions = next(
                (line.split(":", 1)[1].strip() for line in lines if line.startswith("Pre-conditions")), "N/A")
            post_conditions = next(
                (line.split(":", 1)[1].strip() for line in lines if line.startswith("Post-conditions")), "N/A")
            steps_start = next((i for i, line in enumerate(lines) if line.startswith("Steps to Execute")),
                               len(lines))
            results_start = next((i for i, line in enumerate(lines) if line.startswith("Expected Results")),
                                 len(lines))

            steps = "\n".join(lines[steps_start + 1:results_start]).strip() if steps_start < len(lines) else "N/A"
            expected_results = next(
                (line.split(":", 1)[1].strip() for line in lines if line.startswith("Expected Results")), "N/A")

            # Append the row to the sheet
            sheet.append(
                [test_case_id, objective, requirement_covered, design_technique , pre_conditions, post_conditions, steps,
                 expected_results]
                )

    # Save the Excel file to a BytesIO stream
    excel_stream = BytesIO()
    workbook.save(excel_stream)
    excel_stream.seek(0)
    return excel_stream

if st.button("Generate Test Case"):
    final_result = []
    for item in requirements:
        if item['Artifact Type'] == 'SYS Requirement':
            st.text(f"########### Understanding context of Requirement {item['id']} and generating Test scenarios to validate requirement\n")
            result_analysis = orchestrator.process_llm(requirement=item['Primary Text'],count=requirement_count)
            st.text(f"\n###### Analysis ##########\n{result_analysis}")
            temp_result = feedback_loop(result_analysis, EVAL_PROMPT, WORKER_PROMPT)
            final_result.append({'Requirement Covered': item['id'],
                                 'Test Cases':temp_result})
            requirement_count = requirement_count+1

    #st.text(final_result)

    excel_file = create_excel(final_result)
    st.download_button(
            label="Download test cases as excel file",
            data=excel_file.getvalue(),
            file_name="Test_Specification.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )