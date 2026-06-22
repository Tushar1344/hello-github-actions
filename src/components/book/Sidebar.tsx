import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { chapters } from "../../content/chapters";

/** Persistent left navigation: brand, chapter list, credits. */
export function Sidebar() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <aside className="sidebar">
      <NavLink className="brand" to="/">
        <span className="brand-mark">⌁</span>
        Chip Design
      </NavLink>
      <p className="brand-sub">from the bottom up</p>

      {/* compact navigation for the mobile top bar */}
      <select
        className="chapter-select"
        aria-label="Jump to chapter"
        value={pathname}
        onChange={(e) => navigate(e.target.value)}
      >
        <option value="/">Cover</option>
        {chapters.map((c) => (
          <option key={c.slug} value={`/chapter/${c.slug}`}>
            {c.num}. {c.title}
          </option>
        ))}
      </select>

      <p className="nav-label">Book</p>
      <nav className="nav">
        <NavLink to="/" end>
          Cover
        </NavLink>
      </nav>

      <p className="nav-label">Chapters</p>
      <nav className="nav">
        {chapters.map((c) => (
          <NavLink key={c.slug} to={`/chapter/${c.slug}`}>
            <span>{c.title}</span>
            <span className="tag">{c.num}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-foot">
        <p>
          An interactive reconstruction of the
          <br />
          Dwarkesh&nbsp;Patel × Reiner&nbsp;Pope lecture.
        </p>
        <a href="https://www.youtube.com/watch?v=oIk3R-sMX5o" target="_blank" rel="noopener">
          Watch the original →
        </a>
      </div>
    </aside>
  );
}
