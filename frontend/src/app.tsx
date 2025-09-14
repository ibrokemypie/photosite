const term = Deno.env.get("GREETING");

const App = () => {
  return (
    <div>
      <h1>Hello, {term}!</h1>
    </div>
  );
};

export default App;
