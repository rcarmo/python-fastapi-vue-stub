"use strict";
import { createApp, nextTick } from "vue";

createApp({
  data() {
    return {
      message: "Hello Vue!",
      cards: [],
      eventSource: null,
      nextId: 0, // for generating unique IDs
    };
  },
  methods: {
    // Utility method: after DOM updates, scroll .sidebar to its bottom
    scrollSidebarToBottom() {
      nextTick(() => {
        const sidebar = document.querySelector(".sidebar");
        if (sidebar) {
          sidebar.scrollTop = sidebar.scrollHeight;
        }
      });
    },

    async fetchCard() {
      try {
        const response = await fetch("/actions/button");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        console.log("Received /actions/button response:", data);

        // Generate a unique ID for each new card; add highlight
        const card = {
          id: ++this.nextId,
          ...data,
          source: "button",
          highlight: true,
        };
        // Push to the BOTTOM of the array
        this.cards.push(card);

        // Remove highlight after 1 second
        setTimeout(() => {
          card.highlight = false;
        }, 1000);

        // Scroll sidebar to the bottom
        this.scrollSidebarToBottom();
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },

    requestCard() {
      this.fetchCard();
    },

    enableEventSource() {
      if (this.eventSource) {
        console.warn("EventSource is already enabled.");
        return;
      }
      this.eventSource = new EventSource("/events");

      // Listen for "api" events
      this.eventSource.addEventListener("api", (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("Received API event:", data);
          const card = {
            id: ++this.nextId,
            ...data,
            source: "api",
            highlight: true,
          };
          this.cards.push(card);
          setTimeout(() => {
            card.highlight = false;
          }, 1000);
          this.scrollSidebarToBottom();
        } catch (error) {
          console.error("Error parsing API SSE data:", error);
        }
      });

      // Listen for "database" events
      this.eventSource.addEventListener("database", (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("Received Database event:", data);
          const card = {
            id: ++this.nextId,
            ...data,
            source: "database",
            highlight: true,
          };
          this.cards.push(card);
          setTimeout(() => {
            card.highlight = false;
          }, 1000);
          this.scrollSidebarToBottom();
        } catch (error) {
          console.error("Error parsing Database SSE data:", error);
        }
      });

      this.eventSource.onerror = (error) => {
        console.error("EventSource failed:", error);
        this.disableEventSource();
      };
      console.log("EventSource enabled.");
    },

    disableEventSource() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
        console.log("EventSource disabled.");
      } else {
        console.warn("No EventSource to disable.");
      }
    },

    otherAction() {
      alert("Another action triggered!");
    },

    yetAnotherAction() {
      alert("Yet another action!");
    },
  },
  created() {
    // Optionally enable SSE on page load
    // this.enableEventSource();
  },
}).mount("#app");
