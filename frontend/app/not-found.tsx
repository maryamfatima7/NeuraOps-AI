export default function NotFound() {
  return (
    <main className="flex-1 p-8">
      <div className="card p-8 max-w-xl">
        <h1 className="text-2xl font-bold">Page not found</h1>
        <p className="mt-2 text-slate-300">The requested view does not exist in the NeuraOps dashboard.</p>
      </div>
    </main>
  );
}
