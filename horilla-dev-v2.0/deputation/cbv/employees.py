from employee.cbv.employees import EmployeesList

class DeputationEmployeeList(EmployeesList):
    columns = [
        ("Name","get_full_name","get_avatar"),
        ("Department","employee_work_info__department_id"), 
        ("job_position","employee_work_info__job_position_id"), 
        
        
    ]
    records_per_page = 5
    action_method = None
    selected_instances_key_id = "employeeSelectedIds"