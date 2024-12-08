// server.js
const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./config/db");
const axios = require("axios");
const Userroute = require("./Routes/Userroute");
const Productroute = require("./Routes/Productroute");
const SearchHistoryRoute = require("./Routes/SearchHistoryRoute");
const UserInteractionRoute = require("./Routes/UserInteractionRoute");
const { notFound, errorHandler } = require("./middleware/errormiddleware");

dotenv.config();
connectDB();
const app = express();

// Middleware to parse JSON request bodies
app.use(express.json());

// Routes
app.use("/api/user", Userroute);
app.use("/api/products", Productroute); // Mount the product routes
app.use("/api/search-history", SearchHistoryRoute); // Mount the search history route
app.use("/api/user-interactions", UserInteractionRoute);

// Error Handling Middleware
app.use(notFound);
app.use(errorHandler);

const PORT = process.env.PORT || 8000;
app.listen(PORT, console.log(`Server started on port ${PORT}`));
