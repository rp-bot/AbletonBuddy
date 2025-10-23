import { Routes, Route, useParams } from "react-router-dom";
import AppLayout from "./components/Layout/AppLayout";

function App() {
  return (
    <Routes>
      <Route path="/*" element={<AppLayout />} />
    </Routes>
  );
}

export default App;
