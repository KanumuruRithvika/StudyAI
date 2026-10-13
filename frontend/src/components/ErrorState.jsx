export default function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state">
      <div>
        <span className="error-dot">!</span>
        <div>
          <strong>Something went wrong</strong>
          <p>{message || "Please try again."}</p>
        </div>
      </div>
      {onRetry && (
        <button className="button secondary" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
