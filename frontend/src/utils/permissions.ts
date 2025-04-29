/*
 * Permission utilities used across the frontend codebase.
 *
 * This centralises the BusinessPermissions type definition and provides
 * helper functions (e.g. convertFlattenedPermissions) so that all
 * components rely on the same source of truth.
 */

export interface BusinessPermissions {
  navigation: {
    workflows: boolean;
    analytics: boolean;
    settings: boolean;
    api_access: boolean;
    dashboard: boolean;
    clients: boolean;
    voice_setup: boolean;
  };
  analytics: {
    sms: {
      response_time: boolean;
      message_volume: boolean;
      success_rate: boolean;
      cost_per_message: boolean;
      ai_usage: boolean;
      recent_conversations: boolean;
    };
    voice: {
      call_duration: boolean;
      call_volume: boolean;
      success_rate: boolean;
      cost_per_call: boolean;
    };
    email: {
      delivery_rate: boolean;
      open_rate: boolean;
      response_rate: boolean;
      cost_per_email: boolean;
    };
  };
}

/**
 * A fully-false set of permissions convenient for initial states / defaults.
 */
export const DEFAULT_PERMISSIONS: BusinessPermissions = {
  navigation: {
    workflows: false,
    analytics: false,
    settings: false,
    api_access: false,
    dashboard: false,
    clients: false,
    voice_setup: false,
  },
  analytics: {
    sms: {
      response_time: false,
      message_volume: false,
      success_rate: false,
      cost_per_message: false,
      ai_usage: false,
      recent_conversations: false,
    },
    voice: {
      call_duration: false,
      call_volume: false,
      success_rate: false,
      cost_per_call: false,
    },
    email: {
      delivery_rate: false,
      open_rate: false,
      response_rate: false,
      cost_per_email: false,
    },
  },
};

/**
 * Converts a flattened permissions object coming from the database into the
 * nested BusinessPermissions shape expected by the frontend. Keys that do not
 * exist in {@link DEFAULT_PERMISSIONS} are ignored.
 */
export function convertFlattenedPermissions(
  flat: Record<string, any>,
): BusinessPermissions {
  // If the object looks already nested, return a shallow merge to make sure we
  // still include any missing defaults.
  if (typeof flat.navigation === 'object' && typeof flat.analytics === 'object') {
    return {
      ...DEFAULT_PERMISSIONS,
      ...flat,
    } as BusinessPermissions;
  }

  // Clone default so that we never mutate the constant reference.
  const nested: BusinessPermissions = JSON.parse(
    JSON.stringify(DEFAULT_PERMISSIONS),
  );

  Object.entries(flat).forEach(([key, rawValue]) => {
    const value = Boolean(rawValue);
    const parts = key.split('.');

    // navigation.* (two-part key)
    if (parts.length === 2 && parts[0] === 'navigation') {
      const navKey = parts[1] as keyof typeof nested.navigation;
      if (navKey in nested.navigation) {
        (nested.navigation as any)[navKey] = value;
      }
      return;
    }

    // analytics.*.* (three-part key)
    if (parts.length === 3 && parts[0] === 'analytics') {
      const [_, channelKey, metricKey] = parts;
      if ((nested.analytics as any)[channelKey]) {
        (nested.analytics as any)[channelKey][metricKey] = value;
      }
    }
  });

  return nested;
}
