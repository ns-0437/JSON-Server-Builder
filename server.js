// Auto-generated server implementation
const express = require("express");
const cors = require("cors");
const app = express();

app.use(cors({ origin: "*" }));
app.use(express.json());

const authMiddleware = (req, res, next) => {
  if (!req.headers.authorization) {
    return res.status(401).json({ message: "Unauthorized" });
  }
  next();
};

const adminMiddleware = (req, res, next) => {
  if (req.headers.authorization !== "admin") {
    return res.status(403).json({ message: "Forbidden" });
  }
  next();
};

app.post("/login", (req, res) => res.json({ message: "Login successful" }));
app.post("/signup", (req, res) => res.json({ message: "Signup successful" }));
app.post("/signout", (req, res) => res.json({ message: "Signout successful" }));
app.get("/user", authMiddleware, (req, res) => res.json({ message: "User data" }));
app.get("/admin", authMiddleware, adminMiddleware, (req, res) => res.json({ message: "Admin data" }));
app.get("/about", (req, res) => res.json({ message: "About us" }));
app.get("/news", adminMiddleware, (req, res) => res.json({ message: "Latest news" }));
app.get("/blogs", adminMiddleware, (req, res) => res.json({ message: "Blogs list" }));

app.listen(3000, () => console.log("Server running on port 3000"));