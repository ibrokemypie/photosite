const term = Deno.env.get("GREETING");

function App() {
  return <h1>Hello, {term}!</h1>;
}

export default App;
