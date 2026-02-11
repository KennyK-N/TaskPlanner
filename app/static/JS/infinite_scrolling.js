import { text_area_adjust } from "./index.js";

const ERROR = 400;
const FETCH_URL = "http://localhost:5000/retrieve?offset=";
const FAILURE = { status: ERROR };
const cards = document.querySelectorAll(".card_");
const cardContainer = document.querySelector(".card_container_");
const accordionContainer = document.getElementById("content_list_container");

var CanScroll = true;
var OFFSET = 1;

const container = document.getElementById("content_list_container");

const accordionContainerTemplate = `
<div class="accordion accordion-flush card_" id="content_accordion">
  <input
    name="schedule_id"
    type="text"
    value="aa"
    hidden
  />
  <div class="accordion-item">
    <h2 class="accordion-header" id="flush-heading-1">
      <div
        name="accordion_collapse"
        class="accordion-button collapsed d-flex align-items-start justify-content-between"
        data-bs-toggle="collapse"
        data-bs-target="#item_1"
        aria-expanded="false"
        aria-controls="item_1"
        style="cursor: pointer"
      >
        <div class="d-flex flex-column">
          <h5 class="content_title fw-bold mb-0" name="schedule_name">
            Schedule name
          </h5>
          <small class="text-secondary" name="modified_at">
            Jan 20, 2026 • 10:00 AM – 12:00 PM
          </small>
        </div>
      </div> 
    </h2>
    <div
      name="accordion_id"
      id="item_1"
      class="accordion-collapse collapse"
      aria-labelledby="flush-heading-1"
      data-bs-parent="#content_accordion"
    >
      <div class="accordion-body content_text">
      </div>
    </div>
  </div>
</div>
`;

const accordionTaskTemplate = `
<div class="container-fluid pb-4 big-container">
  <div
    class="d-flex align-items-center justify-content-between pb-3"
  >
    <h4 class="mb-0" name="task_name">Task name</h4>
  </div>
  <input type="text" value="asda" name="task_name" hidden />
  <div class="row g-3">
    <div class="col-md-6">
      <div class="floating-container">
        <div class="form-floating">
          <input
            type="time"
            class="form-control"
            id="time_begin"
            value="00:00"
            name="time_begin"
            readonly
          />
          <label for="time_begin" class="form-label"
            >Start Time</label
          >
        </div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="floating-container">
        <div class="form-floating">
          <input
            type="time"
            class="form-control"
            id="time_end"
            value="00:00"
            name="time_end"
            readonly
          />
          <label for="time_end" class="form-label"
            >End Time</label
          >
        </div>
      </div>
    </div>
  </div>
  <p
    class="search-label mb-3"
    id="errorMsg_time_end"
    style="color: red; display: none"
  ></p>
  <div class="row g-6 mt-2">
    <div class="col-md-12">
      <div class="floating-container">
        <div class="form-floating">
          <input
            type="text"
            class="form-control border-0"
            id="location"
            value="Insert location"
            name="location"
            placeholder="Location"
            readonly
          />
          <label for="location">Location</label>
        </div>
      </div>
    </div>
  </div>

  <div class="row g-6 mt-2">
    <div class="col-md-12">
      <div class="floating-container">
        <div class="form">
          <label
            for="description"
            style="position: relative; left: 0.8rem"
            class="form-label text-secondary small"
            >Description</label
          >
          <textarea
            class="form-control border-0"
            id="description"
            name="description"
            placeholder="sas "
            rows="4"
            style="
              white-space: pre-wrap;
              word-break: break-word;
            "
            readonly
          >
          insert text
          </textarea
          >
        </div>
      </div>
    </div>
  </div>
</div>


`;

const ScheduleButtonTemplate = `
<div class="container-fluid pb-4">
  <div
    class="d-flex align-items-center justify-content-start gap-3"
  >
    <div style="width: 400px">
      <div class="floating-container">
        <div class="form-floating">
          <input
            type="date"
            class="form-control border-0"
            name="date"
            id="dateInput"
          />
          <label for="dateInput">Schedule New Date</label>
        </div>
      </div>
    </div>
    <button
      class="fa fa-pencil-alt cercle-icons edit-icon"
      style="border: none; font-size: 1.2rem; color: white"
      onclick="schedule_task(this)"
    ></button>
    <div class="ms-auto">
      <button
        class="far fa-trash-alt cercle-icons delete-icon"
        style="border: none; font-size: 1.2rem; color: white"
        onclick="delete_task(this)"
      ></button>
    </div>
  </div>
</div>
`;

//Animation Observer
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    entry.target.classList.toggle("show", entry.isIntersecting);
    entry.target.classList.toggle("not_show", !entry.isIntersecting);
  });
});

const lastCardObserver = new IntersectionObserver(
  async (entries) => {
    const card = entries[0];
    if (!card.isIntersecting) return;
    await loadNewCards();
    lastCardObserver.unobserve(card.target);
    if (CanScroll) {
      const lastCard = cardContainer.lastElementChild;
      lastCardObserver.observe(lastCard);
    }
  },
  { rootMargin: "50px" },
);

if (cards.length) lastCardObserver.observe(cards[cards.length - 1]);

cards.forEach((card) => {
  observer.observe(card);
});

async function retrieve_doc() {
  try {
    const response = await fetch(`${FETCH_URL}${OFFSET}`);
    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      console.error("Error:", error);
      return FAILURE;
    }
  } catch (error) {
    console.error("Error:", error);
    return FAILURE;
  }
}

async function loadNewCards() {
  if (!CanScroll) return;
  try {
    const query = await retrieve_doc();

    if (query.status != ERROR && query.data.length) {
      for (const record of query.data) {
        const prev_card = accordionContainer.lastElementChild;
        const prev_collapse = prev_card.querySelector(
          "[name=accordion_collapse]",
        );

        const item_value = prev_collapse
          .getAttribute("aria-controls")
          .split("_");

        const new_accordion_item_id = Number(item_value[1]) + 1;
        accordionContainer.insertAdjacentHTML(
          "beforeend",
          accordionContainerTemplate,
        );
        const card = accordionContainer.lastElementChild;

        const accordion_collapse = card.querySelector(
          "[name=accordion_collapse]",
        );

        const accordion_id = card.querySelector("[name=accordion_id]");

        accordion_collapse.setAttribute(
          "data-bs-target",
          `#item_${new_accordion_item_id}`,
        );
        accordion_collapse.setAttribute(
          "aria-controls",
          `#item_${new_accordion_item_id}`,
        );
        card
          .querySelector("input[name=schedule_id]")
          .setAttribute("value", record["id"]);

        card.querySelector("[name=modified_at]").innerText =
          record["modified_at"];

        card.querySelector("[name=schedule_name]").innerText = record["name"];

        accordion_id.id = `item_${new_accordion_item_id}`;

        const accordion_content = card.querySelector(".content_text");

        const task_lst = record.task;

        for (const task of task_lst) {
          accordion_content.insertAdjacentHTML(
            "beforeend",
            accordionTaskTemplate,
          );
          const cur_task = accordion_content.lastElementChild;
          const description = cur_task.querySelector("[name=description]");
          cur_task.querySelector("[name=time_begin]").value = task.time_begin;
          cur_task.querySelector("[name=time_end]").value = task.time_end;
          cur_task.querySelector("[name=location]").value = task.location;
          cur_task.querySelector("h4[name=task_name]").innerText =
            task.task_name;
          cur_task
            .querySelector("input[name=task_name]")
            .setAttribute("value", task.task_name);
          description.value = task.description;
          text_area_adjust(description);
        }
        accordion_content.insertAdjacentHTML(
          "beforeend",
          ScheduleButtonTemplate,
        );
        observer.observe(card);
      }
      OFFSET += 1;
    } else {
      CanScroll = false;
    }
  } catch (error) {
    console.error(error);
  }
}

window.scrollTo(0, 0);
