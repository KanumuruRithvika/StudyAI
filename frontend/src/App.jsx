import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Home from "./pages/Home";
import Setup from "./pages/Setup";
import Plan from "./pages/Plan";
import Dashboard from "./pages/Dashboard";
import Quiz from "./pages/Quiz";
import Adaptation from "./pages/Adaptation";
import Report from "./pages/Report";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/setup" element={<Setup />} />
        <Route path="/plan" element={<Plan />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/adaptation" element={<Adaptation />} />
        <Route path="/report" element={<Report />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
