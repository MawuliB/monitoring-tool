import { useQuery } from '@tanstack/react-query';
import { getPlatforms } from '../api/platforms';

interface PlatformSelectorProps {
  onPlatformSelect: (platform: string) => void;
  selectedPlatform: string | null;
}

interface Platform {
  id: string;
  name: string;
  required_fields: string[];
}

export const PlatformSelector: React.FC<PlatformSelectorProps> = ({
  onPlatformSelect,
  selectedPlatform
}) => {
  const { data: platforms, isLoading } = useQuery<Platform[]>({
    queryKey: ['platforms'],
    queryFn: getPlatforms
  });

  if (isLoading) return <div>Loading platforms...</div>;

  return (
    <div className="platform-selector">
      <h3>Select Platform</h3>
      <div className="platform-buttons">
        {platforms?.map((platform) => (
          <button
            key={platform.id}
            onClick={() => onPlatformSelect(platform.id)}
            className={selectedPlatform === platform.id ? 'active' : ''}
          >
            {platform.name}
          </button>
        ))}
      </div>
    </div>
  );
}; 