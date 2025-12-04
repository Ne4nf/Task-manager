import type { ReactNode } from 'react';

interface StatCardProps {
  icon: ReactNode;
  label: string;
  value: string | number;
  color: 'purple' | 'blue' | 'pink' | 'green';
}

const colorClasses = {
  purple: 'bg-purple-50 border-purple-200 text-purple-600',
  blue: 'bg-blue-50 border-blue-200 text-blue-600',
  pink: 'bg-pink-50 border-pink-200 text-pink-600',
  green: 'bg-green-50 border-green-200 text-green-600',
};

export default function StatCard({ icon, label, value, color }: StatCardProps) {
  const colorClass = colorClasses[color];
  
  return (
    <div className={`${colorClass} bg-white rounded-2xl p-6 fade-in shadow-sm border`}>
      <div className={`${colorClass} mb-3`}>{icon}</div>
      <div className={`text-3xl font-bold ${colorClass} mb-1`}>{value}</div>
      <div className="text-gray-600 text-sm">{label}</div>
    </div>
  );
}
