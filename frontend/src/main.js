import { createApp } from "vue";
import "./style.css";
import { VueDatePicker } from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import App from "./App.vue";
import { router } from "./router";

const app = createApp(App);
app.component("VueDatePicker", VueDatePicker);
app.use(router).mount("#app");
