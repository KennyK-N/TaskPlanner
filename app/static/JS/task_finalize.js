const time_begin_list = document.querySelectorAll("[name='time_begin']");
const time_end_list = document.querySelectorAll("[name='time_end']");
const descriptions = document.getElementsByName("description");
const err_time_msg_list = document.querySelectorAll("#errorMsg_time_end");

function validate_time() {
  const time_begin_val = Array.from(time_begin_list).map(
    (time_node) => time_node.value,
  );

  const time_end_val = Array.from(time_end_list).map(
    (time_node) => time_node.value,
  );

  for (let i = 0; i < time_begin_val.length; i++) {
    const start = time_begin_val[i];
    const end = time_end_val[i];

    if (end <= start) {
      err_time_msg_list[i].style.display = "block";
      err_time_msg_list[i].textContent = `End time must be after start time`;
      console.log(
        `End time must be after start time at index ${i}: ${start} - ${end}`,
      );
      return false;
    }
  }
  return true;
}

function validate_submission() {
  err_time_msg_list.forEach((error_ele) => (error_ele.style.display = "none"));
  const res = validate_time();
  if (!res) return false;

  return true;
}

function adjust_text_area(element) {
  element.style.height = "1px";
  element.style.height = 25 + element.scrollHeight + "px";
}

for (description of descriptions) {
  adjust_text_area(description);
}

function delete_element(e) {
  const tasks = document.querySelectorAll(".big-container");
  if (tasks.length != 1) e.parentElement.parentElement.remove();
}
