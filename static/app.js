"use strict";
import { createApp, nextTick } from "vue";

createApp({
  data() {
    return {
      message: "Hello Vue!",
      cards: [],
      eventSource: null,
      nextId: 0, // for generating unique IDs
      connectionId: null, // to store our unique connection ID from the server
    };
  },
  methods: {
    async generatePDF() {
      try {
        // Open in new tab first (better UX as PDF generation might take time)
        const newTab = window.open("about:blank");

        // Fetch PDF
        const response = await fetch("/generate-pdf");
        if (!response.ok) {
          throw new Error("Failed to generate PDF");
        }

        // Get the PDF blob
        const blob = await response.blob();

        // Create object URL
        const pdfUrl = URL.createObjectURL(blob);

        // Navigate the new tab to the PDF
        newTab.location.href = pdfUrl;

        // Clean up the object URL after a delay
        setTimeout(() => URL.revokeObjectURL(pdfUrl), 1000);
      } catch (error) {
        console.error("Error generating PDF:", error);
        alert("Failed to generate PDF. Please try again.");
      }
    },

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
      // Create a new EventSource connection
      this.eventSource = new EventSource("/events");

      // Listen for "connect" event to capture the connection ID from server.
      this.eventSource.addEventListener("connect", (event) => {
        try {
          const data = JSON.parse(event.data);
          this.connectionId = data.connectionId;
          console.log("Connected with ID:", this.connectionId);
        } catch (error) {
          console.error("Error parsing connection data:", error);
        }
      });

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
        console.error("EventSource error:", error);
        this.disableEventSource();
      };

      console.log("EventSource enabled.");
    },

    disableEventSource() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
        this.connectionId = null;
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
    // Optionally enable SSE on page load:
    // this.enableEventSource();
  },
}).mount("#app");
