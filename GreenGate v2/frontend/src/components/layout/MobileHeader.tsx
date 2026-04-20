import { Menu } from 'lucide-react';
import { useAppStore } from '../../store/appStore';

export function MobileHeader() {
  const toggleSidebar = useAppStore((s) => s.toggleSidebar);

  return (
    <div className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-[var(--color-primary)] text-white h-14 flex items-center px-4 shadow-md">
      <button onClick={toggleSidebar} className="p-2 rounded-lg hover:bg-white/10">
        <Menu className="w-5 h-5" />
      </button>
      <span
        className="ml-3 text-lg font-semibold"
        style={{ fontFamily: 'var(--font-display)' }}
      >
        SustainGate
      </span>
    </div>
  );
}
