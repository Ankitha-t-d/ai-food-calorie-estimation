import { useEffect, useState } from "react";
import "./App.css";
import Dashboard from "./Dashboard";

function App() {

  const [showSplash, setShowSplash] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [isRegister, setIsRegister] = useState(false);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------------------
  // SPLASH SCREEN
  // -----------------------------------------

  useEffect(() => {

    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 2500);

    return () => clearTimeout(timer);

  }, []);


  // -----------------------------------------
  // LOGIN / SIGNUP
  // -----------------------------------------

  const handleSubmit = async (event) => {

    event.preventDefault();

    setError("");

    if (!username || !password) {
      setError(
        "Please enter username and password."
      );
      return;
    }

    if (
      isRegister &&
      password !== confirmPassword
    ) {
      setError(
        "Passwords do not match."
      );
      return;
    }

    setLoading(true);

    try {

      const API_URL = "https://ai-food-calorie-estimation.onrender.com";

      const endpoint = isRegister
         ? `${API_URL}/signup`
        : `${API_URL}/login`;

      const response = await fetch(
        endpoint,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            username: username,
            password: password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Something went wrong."
        );

      }

      if (isRegister) {

        alert(
          "Account created successfully!"
        );

        setIsRegister(false);
        setUsername("");
        setPassword("");
        setConfirmPassword("");

      } else {

        alert("Login successful!");

        setIsLoggedIn(true);

      }

    } catch (error) {

      setError(error.message);

    }

    setLoading(false);
  };


  // -----------------------------------------
  // SPLASH PAGE
  // -----------------------------------------

  if (showSplash) {

    return (
      <div className="splash-screen">

        <div className="splash-content">

          <div className="splash-logo">
            🍲
          </div>

          <h1>
            Food20
          </h1>

          <p>
            AI-Powered Food Calorie Estimation
          </p>

        </div>

      </div>
    );
  }


  // -----------------------------------------
  // DASHBOARD
  // -----------------------------------------

  if (isLoggedIn) {

    return <Dashboard />;

  }


  // -----------------------------------------
  // LOGIN / REGISTER
  // -----------------------------------------

  return (

    <div className="login-page">

      <div className="login-card">


        <h1>
          {isRegister
            ? "Create account"
            : "Welcome"}
        </h1>

        <p className="subtitle">

          {isRegister
            ? "Create your Food20 account"
            : "Login to continue to your nutrition dashboard."}

        </p>

        <form onSubmit={handleSubmit}>

          <label>
            Username
          </label>

          <input
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(event) =>
              setUsername(
                event.target.value
              )
            }
          />

          <label>
            Password
          </label>

          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(event) =>
              setPassword(
                event.target.value
              )
            }
          />

          {isRegister && (

            <>

              <label>
                Confirm Password
              </label>

              <input
                type="password"
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(
                    event.target.value
                  )
                }
              />

            </>

          )}

          {error && (

            <div className="error">
              {error}
            </div>

          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >

            {loading
              ? isRegister
                ? "Creating account..."
                : "Logging in..."
              : isRegister
              ? "Create account"
              : "Login"}

          </button>

        </form>

        <div className="switch-text">

          {isRegister
            ? "Already have an account?"
            : "Don't have an account?"}

          <button
            className="switch-button"
            onClick={() => {

              setIsRegister(
                !isRegister
              );

              setError("");
              setUsername("");
              setPassword("");
              setConfirmPassword("");

            }}
          >

            {isRegister
              ? "Login"
              : "Create account"}

          </button>

        </div>

      </div>

    </div>

  );
}

export default App;