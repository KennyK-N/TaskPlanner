MAX_PROMPT = 5;

const input = document.getElementById("itemsInput");
const errorMsg = document.querySelectorAll("#errorMsg");
const button = document.getElementById("promptSubmit");
const date = document.getElementById("dateInput");
const location_checkbox = document.getElementById("locationCheckbox");
const schedule_name = document.getElementById("schedule_name");

location_checkbox.checked = false;

function checkform() {
  errorMsg.forEach((error_ele) => (error_ele.style.display = "none"));

  const clean = DOMPurify.sanitize(input.value);

  const items = clean
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item !== "");

  const date_value = date.value;
  const schedule_name_value = schedule_name.value;
  const location_checkbox_value = location_checkbox.checked;

  if (items.length > MAX_PROMPT) {
    errorMsg[0].style.display = "block";
    errorMsg[0].textContent = `You can enter a maximum of ${MAX_PROMPT} items.`;
    console.log(items, date_value, location_checkbox_value);
    return false;
  } else if (items.length == 0) {
    errorMsg[0].style.display = "block";
    errorMsg[0].textContent = "Textbox Cannot be empty";
    return false;
  } else if (!date_value) {
    errorMsg[1].style.display = "block";
    errorMsg[1].textContent = "Date Cannot be empty";
    return false;
  } else if (!schedule_name_value) {
    errorMsg[2].style.display = "block";
    errorMsg[2].textContent = "The name of the Schedule cannot be empty";
    return false;
  }

  input.value = items;
  return true;
}
