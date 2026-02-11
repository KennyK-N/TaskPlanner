const descriptions = document.getElementsByName("description");
const DELETE_URL = "http://localhost:5000/delete?TaskId=";
const SCHEDULE_URL = "http://localhost:5000/create_google_schedule?TaskId=";
const notification_template = `
<div class="alert alert-dismissible fade show" role="alert">
  <div class="aui-message closeable">
  </div>
</div>
`;

const notification_close_button = `    
<span
  class="aui-icon icon-close fa fa-close"
  data-bs-dismiss="alert"
  aria-label="Close"
  role="button"
  tabindex="0"
  style="color: black"
></span>
`;

function text_area_adjust(element) {
  element.style.height = element.value.length * 0.02 + "rem";
}

async function delete_task(element) {
  const old_alert = document.querySelector(".alert");
  if (old_alert) old_alert.remove();

  try {
    const accordion = element.closest(".accordion");
    const id = Number(accordion.querySelector('[name="schedule_id"]').value);

    const response = await fetch(`${DELETE_URL}${id}`, { method: "DELETE" });
    const data = await response.json();
    const text = data.message;
    if (!data.success) throw new Error(text);

    accordion.remove();

    document
      .querySelector("#content_list_container")
      .insertAdjacentHTML("afterbegin", notification_template);
    const inner_content = document.querySelector(".aui-message");
    inner_content.classList.add("success");
    const text_node = document.createTextNode(text);
    inner_content.appendChild(text_node);
    inner_content.insertAdjacentHTML("afterbegin", notification_close_button);
  } catch (error) {
    console.error(error);

    document
      .querySelector("#content_list_container")
      .insertAdjacentHTML("afterbegin", notification_template);
    const inner_content = document.querySelector(".aui-message");
    inner_content.classList.add("error");
    const text_node = document.createTextNode("Failed to delete current task");
    inner_content.appendChild(text_node);
    inner_content.insertAdjacentHTML("afterbegin", notification_close_button);
  }
}

async function schedule_task(element) {
  const old_alert = document.querySelector(".alert");
  if (old_alert) old_alert.remove();

  try {
    const accordion = element.closest(".accordion");
    const id = Number(accordion.querySelector('[name="schedule_id"]').value);

    const date = accordion.querySelector("[name=date]").value;
    if (!date) throw new Error("Date cannot be empty");

    const response = await fetch(`${SCHEDULE_URL}${id}&date=${date}`, {
      method: "POST",
    });
    const data = await response.json();
    const text = data.message;
    if (!data.success) throw new Error(text);

    document
      .querySelector("#content_list_container")
      .insertAdjacentHTML("afterbegin", notification_template);
    const inner_content = document.querySelector(".aui-message");
    inner_content.classList.add("success");
    const text_node = document.createTextNode(text);
    inner_content.appendChild(text_node);
    inner_content.insertAdjacentHTML("afterbegin", notification_close_button);
  } catch (error) {
    console.error(error);

    document
      .querySelector("#content_list_container")
      .insertAdjacentHTML("afterbegin", notification_template);
    const inner_content = document.querySelector(".aui-message");
    inner_content.classList.add("error");
    const text_node = document.createTextNode(
      "Failed to schedule current task",
    );
    inner_content.appendChild(text_node);
    inner_content.insertAdjacentHTML("afterbegin", notification_close_button);
  }
}

for (var i = 0; i < descriptions.length; i++) {
  text_area_adjust(descriptions[i]);
}

export { text_area_adjust };
window.schedule_task = schedule_task;
window.delete_task = delete_task;
