import { useQuery } from '@tanstack/react-query'
import { readOwnProfileProfilesGet } from '@/lib/api/generated/profiles/profiles'

export function useProfile() {
  return useQuery({
    queryKey: ['profile'],
    queryFn: () => readOwnProfileProfilesGet(),
  })
}
